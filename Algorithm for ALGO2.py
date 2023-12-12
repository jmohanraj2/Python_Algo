

Stage 1 (No Open Positions and open_orders == 3) or (Prc == TRGT and prc == Price2 and prc == price3 and and open_orders == 3)
************************************************************************
S1 - All three open Buy Orders. No positions. DONE

S2 - 2 Buy Orders(NA),1 Sell Order(Q1_T) and  1 Positios  : LTP>AVG 

QTY1
Target = Targer_Price


Stage 2 (Prc == SLP2 and prc == Price3 and open_orders == 2 ) or (Prc == TRGT and prc == price3 and open_orders == 2)
************************************************************************
S1 - 1 - Buy Order, 1 SL Order2(Q2_SLP2) and  1 Position :LTP<AVG
S2 - 1 - Buy Order, 1 Sell Order(Q2_T) and  1 Position :LTP>AVG

QTY2
SLPRICE2
Target = Targer_Price


Stage 3 (Prc == SLP3 and open_orders == 1) or (Prc == TRGT and open_orders == 1) 
*****************************************************************************
S1 - 1 SL Order3 (Q3_SLP3) and  1 Position :LTP<AVG
S2 - 1 Sell Order(Q3_T) and  1 Position :LTP>AVG

QTY3
SLPRICE3
Target = Targer_Price