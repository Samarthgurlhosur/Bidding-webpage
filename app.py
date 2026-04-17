from flask import Flask, render_template, request, redirect, flash, jsonify
from models import db, Team, Item, Bid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'your-secret-key'
db.init_app(app)

with app.app_context():
    db.create_all()

# Home Dashboard
@app.route('/')
def index():
    teams = Team.query.all()
    items = Item.query.all()
    auctioned_items = Item.query.filter(Item.sold_to.isnot(None)).all()
    available_items = Item.query.filter_by(is_auctioned=False, sold_to=None).all()
    
    return render_template('index.html', 
                         teams=teams, 
                         items=items,
                         auctioned_items=auctioned_items,
                         available_items=available_items)

# Add Team
@app.route('/add_team', methods=['GET', 'POST'])
def add_team():
    if request.method == 'POST':
        name = request.form['name']
        points = int(request.form.get('points', 1000))
        
        existing = Team.query.filter_by(name=name).first()
        if existing:
            flash(f'Team {name} already exists!', 'error')
            return redirect('/add_team')
        
        team = Team(name=name, points=points)
        db.session.add(team)
        db.session.commit()
        flash(f'Team {name} added with {points} points!', 'success')
        return redirect('/')
    return render_template('add_team.html')

# Add Tool or Algorithm
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        item_type = request.form['item_type']  # 'tool' or 'algorithm'
        price = int(request.form['price'])
        
        item = Item(name=name, item_type=item_type, base_price=price)
        db.session.add(item)
        db.session.commit()
        flash(f'{item_type.capitalize()} "{name}" added with base price {price}!', 'success')
        return redirect('/')
    return render_template('add_item.html')

# Auction Page - One item at a time
@app.route('/auction')
def auction():
    # Get current item being auctioned
    current_item = Item.query.filter_by(is_auctioned=True).first()
    
    # If no current auction, auto-start the next unsold item
    if not current_item:
        next_item = Item.query.filter_by(is_auctioned=False, sold_to=None).first()
        if next_item:
            next_item.is_auctioned = True
            db.session.commit()
            current_item = next_item
    
    teams = Team.query.all()
    bids = []
    highest_bid = None
    highest_bidder = None
    upcoming_items = Item.query.filter_by(is_auctioned=False, sold_to=None).all()
    
    if current_item:
        bids = Bid.query.filter_by(item_id=current_item.id).order_by(Bid.bid_amount.desc()).all()
        if bids:
            highest_bid = bids[0]
            highest_bidder = highest_bid.team
    
    available_items = len(upcoming_items)
    
    return render_template('auction.html', 
                         current_item=current_item,
                         teams=teams,
                         bids=bids,
                         highest_bid=highest_bid,
                         highest_bidder=highest_bidder,
                         available_items=available_items,
                         upcoming_items=upcoming_items)

# Place Bid
@app.route('/place_bid', methods=['POST'])
def place_bid():
    try:
        team_id = int(request.form['team_id'])
        item_id = int(request.form['item_id'])
        bid_amount = int(request.form['bid_amount'])
        
        team = Team.query.get(team_id)
        item = Item.query.get(item_id)
        
        if not team or not item:
            flash('Invalid team or item!', 'error')
            return redirect('/auction')
        
        # Determine the minimum valid bid: base price or higher than the current highest bid
        existing_bids = Bid.query.filter_by(item_id=item_id, team_id=team_id).order_by(Bid.bid_amount.desc()).all()
        current_highest_bid = existing_bids[0].bid_amount if existing_bids else 0
        overall_highest_bid = Bid.query.filter_by(item_id=item_id).order_by(Bid.bid_amount.desc()).first()
        next_minimum_bid = item.base_price
        if overall_highest_bid:
            next_minimum_bid = max(item.base_price, overall_highest_bid.bid_amount + 1)

        if bid_amount < next_minimum_bid:
            if overall_highest_bid:
                flash(f'Bid must be at least {next_minimum_bid} points and higher than the current highest bid of {overall_highest_bid.bid_amount} points!', 'error')
            else:
                flash(f'Bid must be at least {item.base_price} points (base price)!', 'error')
            return redirect('/auction')

        if bid_amount <= current_highest_bid:
            flash(f'{team.name} must bid higher than your current bid of {current_highest_bid} points!', 'error')
            return redirect('/auction')
        
        additional_amount = bid_amount - current_highest_bid
        
        if team.points < additional_amount:
            flash(f'{team.name} does not have enough points! Available: {team.points}, Need additional: {additional_amount}', 'error')
            return redirect('/auction')
        
        # Deduct additional points from team
        team.points -= additional_amount
        
        # If this is an update to existing bid, we don't need to refund since we're only charging the difference
        # Create new bid (multiple bids allowed)
        new_bid = Bid(item_id=item_id, team_id=team_id, bid_amount=bid_amount)
        db.session.add(new_bid)
        db.session.commit()
        
        flash(f'{team.name} bid {bid_amount} for {item.name}! Remaining points: {team.points}', 'success')
    except Exception as e:
        flash(f'Error placing bid: {str(e)}', 'error')
    
    return redirect('/auction')

# End Auction for current item
@app.route('/end_auction/<int:item_id>', methods=['POST'])
def end_auction(item_id):
    item = Item.query.get(item_id)
    if not item:
        flash('Item not found!', 'error')
        return redirect('/auction')
    
    # Get highest bid
    highest_bid = Bid.query.filter_by(item_id=item_id).order_by(Bid.bid_amount.desc()).first()
    
    if highest_bid:
        # Award to winning team
        item.sold_to = highest_bid.team_id
        item.final_price = highest_bid.bid_amount
        item.is_auctioned = False
        
        # Get all unique teams that bid on this item
        bidding_teams = db.session.query(Bid.team_id).filter_by(item_id=item_id).distinct().all()
        
        # Refund points to losing bidders (they were charged their highest bid amount)
        for (team_id,) in bidding_teams:
            if team_id != highest_bid.team_id:
                # Find the highest bid amount for this losing team
                highest_losing_bid = Bid.query.filter_by(item_id=item_id, team_id=team_id).order_by(Bid.bid_amount.desc()).first()
                if highest_losing_bid:
                    highest_losing_bid.team.points += highest_losing_bid.bid_amount
        
        # Winner keeps their deduction (already deducted when they bid)
        team = highest_bid.team
        
        db.session.commit()
        flash(f'{team.name} won {item.name} for {highest_bid.bid_amount} points! Remaining points: {team.points}', 'success')
    else:
        # No winner, refund all bidders their highest bid amounts
        bidding_teams = db.session.query(Bid.team_id).filter_by(item_id=item_id).distinct().all()
        for (team_id,) in bidding_teams:
            highest_bid_for_team = Bid.query.filter_by(item_id=item_id, team_id=team_id).order_by(Bid.bid_amount.desc()).first()
            if highest_bid_for_team:
                highest_bid_for_team.team.points += highest_bid_for_team.bid_amount
        
        flash(f'No bids on {item.name}. Item remains unsold. All points refunded.', 'warning')
        item.is_auctioned = False
        db.session.commit()
    
    # Auto-start next auction
    next_item = Item.query.filter_by(is_auctioned=False, sold_to=None).first()
    if next_item:
        next_item.is_auctioned = True
        db.session.commit()
        flash(f'Auction started for: {next_item.name}', 'success')
    
    return redirect('/auction')

# Start Auction for next item
@app.route('/start_next_auction', methods=['POST'])
def start_next_auction():
    # Find next unsold item
    next_item = Item.query.filter_by(is_auctioned=False, sold_to=None).first()
    
    if next_item:
        next_item.is_auctioned = True
        db.session.commit()
        flash(f'Auction started for: {next_item.name}', 'success')
    else:
        flash('No more items to auction!', 'warning')
    
    return redirect('/auction')

# Reset all auction data
@app.route('/reset', methods=['POST'])
def reset_all():
    Bid.query.delete()
    Item.query.delete()
    Team.query.delete()
    db.session.commit()
    flash('All auction data has been cleared. Start fresh now.', 'success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)