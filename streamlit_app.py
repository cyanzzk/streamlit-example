import streamlit as st
import pandas as pd



# Big title of the dashboard

up_load_or_not = st.checkbox('Upload RFQ Data Manually?', value=False)
if up_load_or_not:
    file = st.file_uploader("Upload RFQ Data (.csv)")
    data = pd.read_csv(file)
else:
    data = pd.read_csv('file.csv')

st.title('RFQ Data Visualization')




#.............Data Cleaning and Prep...............
# data = pd.read_csv('file.csv')
data = data.iloc[14:,:]

data['datetime'] = pd.to_datetime(data['timestamp'], unit='s')
data['date'] = data['datetime'].dt.normalize()

data = data.drop(columns=['createTime','updateTime'])

filter_date = st.text_input('Enter the date to filter data after', '2024-01-01')

# Filter data after a certain date
data = data[data['date'] >= pd.Timestamp(filter_date)]
data





# Make buy and sell binary, 1 indicates buy, 0 indicates sell
data['buy_flag'] = data['direction'].apply(lambda x: 1 if x == 'BUY' else 0)

# Mutate one column that shows cumulative dynamic fees.
data['cumulative_dynamic_fees_unsettled'] = data['dynamic_fees_in_usdt'].cumsum()

# Mutate one column that shows dynamic fees deducted NAV.
data['adjusted_nav'] = data['nav'] - data['cumulative_dynamic_fees_unsettled']

data['volume'] = abs(data['onchain_usdt_amount'])


days_elapsed = (data['datetime'].max() - data['datetime'].min()).days

cumulative_pnl_all_time = data['order_final_pnl'].sum()
cumulative_dynamic_fees_all_time = data['dynamic_fees_in_usdt'].sum()
cumulative_cex_fees_all_time = data['cex_commission_fees_in_usdt'].sum()

#....................Basic Data Analysis.....................

aggregated_data = data.groupby('date').agg({'dynamic_fees_in_usdt': 'sum', 'cex_commission_fees_in_usdt': 'sum','orderHash':'count','buy_flag':'sum','order_final_pnl': 'sum','volume':'sum'})
aggregated_data['nums_of_order'] = aggregated_data['orderHash']
aggregated_data['buy_ratio'] = aggregated_data['buy_flag'] / aggregated_data['nums_of_order']

aggregated_data['daily_pnl_to_volume'] = 100*aggregated_data['order_final_pnl'] / aggregated_data['volume']



st.header('Aggregated Data')
st.dataframe(aggregated_data)


#....................Token Data Analysis.....................
token_aggregated_data = data.groupby('symbol').agg({'dynamic_fees_in_usdt': 'sum', 'cex_commission_fees_in_usdt': 'sum','orderHash':'count','buy_flag':'sum','order_final_pnl': 'sum','volume':'sum'})


st.header('Token Aggregated Data')
st.dataframe(token_aggregated_data)






#....................Visualization.....................

st.header('Input Principal Amount')
principal_amount = st.number_input('Enter the principal amount', value=200000)

st.header('Cumulative Values')
st.write(f'Cumulative PnL: {cumulative_pnl_all_time} USDT;')
st.write(f'Cumulative Dynamic Fees: {cumulative_dynamic_fees_all_time} USDT;')
st.write(f'Cumulative CEX Fees: {cumulative_cex_fees_all_time} USDT;')
st.write(f'Cumulative PnL%: {cumulative_pnl_all_time/principal_amount*100}%;')
st.write(f'Corresponding APR: {(cumulative_pnl_all_time/principal_amount*100)/days_elapsed*365}%;')





st.header('Cumulative of order_final_pnl')
st.line_chart(data['order_final_pnl'].cumsum())

st.header('Cumulative of dynamic_fees_in_usdt')
st.line_chart(data['dynamic_fees_in_usdt'].cumsum())


st.header('dynamic fees')
st.bar_chart(aggregated_data['dynamic_fees_in_usdt'])

st.header('order_final_pnl')
st.bar_chart(aggregated_data['order_final_pnl'])

st.header('buy_ratio')
st.line_chart(aggregated_data['buy_ratio'])

st.header('nums_of_order')
st.bar_chart(aggregated_data['nums_of_order'])

st.header('volume')
st.bar_chart(aggregated_data['volume'])

st.header('daily_pnl_to_volume(in %)')
st.line_chart(aggregated_data['daily_pnl_to_volume'])

# add a column that calculates the moving average of cex_abs_order_usdt_amount of 7 days
ma_window_size = st.number_input('Enter the MA Window Size', value=7)

aggregated_data['volume_ma'] = aggregated_data['volume'].rolling(window=ma_window_size).mean()

st.header('Volume MA Line')
st.bar_chart(aggregated_data['volume_ma'])



# add a column that calculates the moving average of order_final_pnl of 7 days

aggregated_data['order_final_pnl_ma'] = aggregated_data['order_final_pnl'].rolling(window=ma_window_size).mean()

st.header('order_final_pnl MA Line')
st.line_chart(aggregated_data['order_final_pnl_ma'])
