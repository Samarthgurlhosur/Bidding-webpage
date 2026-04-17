# 🏆 Bidding Website System

A complete web-based auction system where teams can bid on tools and algorithms. The system tracks team points, manages real-time bidding, and awards items to winning teams.

## Features

✨ **Core Features:**
- ✅ Add teams with custom starting points
- ✅ Add tools and algorithms to the inventory
- ✅ One-by-one auction display system
- ✅ Real-time bidding with live updates (auto-refresh every 3 seconds)
- ✅ Team points tracking and deduction
- ✅ Automatic bid validation (minimum bid = base price or current highest bid + 1)
- ✅ Auction history and winner tracking
- ✅ Beautiful, responsive UI with modern styling

🎯 **Auction Features:**
- View current item being auctioned with all details
- See real-time highest bid and bidder
- View all bids for current item with timestamps
- Medal rankings (🥇 🥈 🥉) for top bidders
- Auto-award items to winning teams
- Deduct points from winning team automatically
- Move to next item automatically after auction ends

📊 **Dashboard Features:**
- View all teams with their points and items won
- See items they've won with their final prices
- Browse available items and auction history
- Track overall system statistics

## Installation & Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

The application will start at `http://localhost:5000`

## How to Use

### Step 1: Add Teams
1. Go to **Add Team** page
2. Enter team name and starting points (default: 1000)
3. Click **Add Team**

### Step 2: Add Items (Tools/Algorithms)
1. Go to **Add Item** page
2. Enter item name
3. Select type (Tool or Algorithm)
4. Set base price in points
5. Click **Add Item**

### Step 3: Start Auction
1. Go to **Auction** page
2. Click **Start Auction** to begin auctioning the first item
3. Teams select their team name from dropdown
4. Teams enter their bid amount (must be ≥ base price for first bid)
5. Subsequent bids must be higher than current highest bid
6. Page auto-refreshes every 3 seconds to show live updates

### Step 4: End Auction & Award Item
1. Once bidding is complete, click **End Auction & Award Item**
2. System automatically:
   - Awards item to team with highest bid
   - Deducts bid amount from team's points
   - Moves to next item ready for auction

### Step 5: Monitor Progress
- Check **Dashboard** to see:
  - All teams and their remaining points
  - Items each team has won
  - Auction history with final prices

## File Structure

```
Bid/
├── app.py                 # Flask application with routes
├── models.py             # Database models (Team, Item, Bid)
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── database.db           # SQLite database (auto-created)
├── static/
│   └── style.css         # Responsive CSS styling
└── templates/
    ├── index.html        # Dashboard/Home page
    ├── add_team.html     # Add team form
    ├── add_item.html     # Add tool/algorithm form
    └── auction.html      # Live auction interface
```

## Database Models

### Team
- `id`: Primary key
- `name`: Team name (unique)
- `points`: Current team points
- `items_won`: Relationship to items owned

### Item
- `id`: Primary key
- `name`: Item name
- `item_type`: 'tool' or 'algorithm'
- `base_price`: Starting bid price
- `sold_to`: Foreign key to Team (who won it)
- `final_price`: Price at which item was sold
- `is_auctioned`: Currently being auctioned?
- `created_at`: Timestamp

### Bid
- `id`: Primary key
- `item_id`: Foreign key to Item
- `team_id`: Foreign key to Team
- `bid_amount`: Bid amount in points
- `timestamp`: When bid was placed
- `team`: Relationship to Team
- `item`: Relationship to Item

## Key Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Dashboard home page |
| `/add_team` | GET, POST | Add new team |
| `/add_item` | GET, POST | Add new tool/algorithm |
| `/auction` | GET | View live auction |
| `/place_bid` | POST | Place a bid on current item |
| `/end_auction/<item_id>` | POST | End auction & award item |
| `/start_next_auction` | POST | Start auction for next item |

## Bidding Rules

1. **Minimum Bid**: 
   - First bid: Must be ≥ base price
   - Subsequent bids: Must be > current highest bid

2. **Team Points Check**:
   - Team must have enough points for their bid
   - Points are deducted when they win (end of auction)

3. **One Item at a Time**:
   - Only one item can be auctioned at once
   - Must explicitly start next auction after previous one ends

4. **Auto-Award**:
   - When auction ends, highest bidder automatically wins
   - Points are automatically deducted from winning team

## Tips & Best Practices

💡 **For Running Smooth Auctions:**
- Start with reasonable base prices
- Allocate similar starting points to teams for fair competition
- Give teams enough time to bid (page auto-refreshes every 3 seconds)
- Check bid history window for past bids and timestamps
- Use "End Auction & Award Item" button when bidding is complete

📱 **Responsive Design:**
- Works on desktop, tablet, and mobile
- Touch-friendly buttons and forms
- Auto-scaling layouts

🎨 **Customization:**
- Edit `static/style.css` to change colors and fonts
- Modify Flask routes in `app.py` to add new features
- Update templates to customize the UI

## Troubleshooting

**Issue**: "Database is locked" error
- Solution: Close all connections and restart the app

**Issue**: Items not appearing in auction
- Solution: Make sure you clicked "Add Item" and items were saved

**Issue**: Bids not updating in real-time
- Solution: Page auto-refreshes every 3 seconds; page may need manual refresh

**Issue**: Can't place bid
- Solution: Check if team has enough points; check if bid meets minimum

## Future Enhancements

Potential features to add:
- User authentication & login
- Timed auctions (countdown timer)
- Starting bid increment suggestions
- Bid cancellation/modification
- Export auction results to CSV
- Admin panel for managing items
- Automated bidding (proxy bidding)
- Email notifications for winning bids

## License

Free to use and modify for your needs!

## Support

For issues or questions about this bidding system, check the code comments in:
- `app.py` - Main application logic
- `models.py` - Database structure
- `templates/auction.html` - Auction interface

---

**Built with Flask + SQLAlchemy + Modern CSS**

Happy Bidding! 🎉
