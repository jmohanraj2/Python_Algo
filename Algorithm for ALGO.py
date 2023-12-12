if position is NULL and order is NULL (or) postion qty is == order qty:
    Pass/Do Nothing
Else:
    if position is NULL and order is "NOT NULL":
        order_id = Client.order_Report()
        client.Cancel_order(order_id)
    elif position is "NOT NULL" and order is NULL:
        Get Position details, Check LTP vs AVG_Price and place STPLOSS/PROFIT order
        
        
        
#Get Position details and place STPLOSS order

if LTP > AVG_Price:
    cancel existing Open STPLOSS SELL orders AND
    Place Profit Orders
elif LTP < AVG_Price:
    cancel existing Open PROFIT/ STPLOSS SELL orders AND
    Place STPLOSS orders
    
    
#PLACE STPLOSS orders
if position Quantity == QTY2:
    cancel existing PROFIT SELL orders AND
    Place SLP order for QTY2 # First STPLOSS order
elif position Quantity == QTY3:
    cancel existing PROFIT SELL orders (or) PROFIT orders AND
    Place SLP order for QTY3 #Second STPLOSS order
    

1. Buy QTY1 and Profit booked.
2. Buy QTY1 and QTY2 and place STPLOSS order
3. Buy QTY1 and QTY2 and profit booked
4. Buy QTY1 and QTY2 and QTY3 and place STPLOSS order
5. Buy QTY1 and QTY2 and QTY3 and profit booked
    
    
    