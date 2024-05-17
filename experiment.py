import requests
import pandas as pd
import numpy as np
import time
import xlwings as xw
from bs4 import BeautifulSoup
import datetime
import streamlit as st
st.set_page_config(page_title="Dashboard", layout="wide")

TWO_PERCENT_MARKET_PRICE = 0.0


# get the last thursday of the current month
def last_thursday_version_2(year, month):
    if month == 1 or month == 2 or month == 3 or month == 4 or month == 5 or month == 6 or month == 7 or month == 8 or month == 9:
        date = f"{year}-0{month}-01"
    if month == 10 or month == 11 or month == 12:
        date = f"{year}-{month}-01"

    # we have a datetime series in our dataframe...
    df_Month = pd.to_datetime(date)

    # we can easily get the month's end date:
    df_mEnd = df_Month + pd.tseries.offsets.MonthEnd(1)

    # Thursday is weekday 3, so the offset for given weekday is
    offset = (df_mEnd.weekday() - 3) % 7

    # now to get the date of the last Thursday of the month, subtract it from
    # month end date:
    df_Expiry = df_mEnd - pd.to_timedelta(offset, unit='D')

    return df_Expiry


# get the last thursday of the next month
def last_thursday(year, month):
    if month == 12:
        date = f"{year + 1}-01-01"
    if month == 1 or month == 2 or month == 3 or month == 4 or month == 5 or month == 6 or month == 7 or month == 8:
        date = f"{year}-0{month + 1}-01"
    if month == 9 or month == 10 or month == 11:
        date = f"{year}-{month + 1}-01"

    # we have a datetime series in our dataframe...
    df_Month = pd.to_datetime(date)

    # we can easily get the month's end date:
    df_mEnd = df_Month + pd.tseries.offsets.MonthEnd(1)

    # Thursday is weekday 3, so the offset for given weekday is
    offset = (df_mEnd.weekday() - 3) % 7

    # now to get the date of the last Thursday of the month, subtract it from
    # month end date:
    df_Expiry = df_mEnd - pd.to_timedelta(offset, unit='D')

    return df_Expiry



exchange = "NSE"


def current_market_price(ticker, exchange):
    url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"

    for _ in range(1000000):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        class1 = "YMlKec fxKbKc"

        price = float(soup.find(class_=class1).text.strip()[1:].replace(",", ""))
        yield price

        time.sleep(5)


def get_dataframe(ticker):
    while True:
        try:

            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={ticker}"
            headers = {"accept-encoding": "gzip, deflate, br, zstd",
                       "accept-language": "en-US,en;q=0.9",
                       "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                       "cookie": '_ga=GA1.1.1104812566.1715673932; nseQuoteSymbols=[{"symbol":"ACC","identifier":null,"type":"equity"}]; _abck=AC0A6E579954CFC1BA4A76B56A1628F3~0~YAAQUGDQF0wwS4OPAQAAvT0/hQs1V3VnOWk4E0y2ERf8giXghMD7ExTgmy5Tz7+VVIQnIXRyq0HAhyhGF2vjKxzrr+GITJqy4CoFAXMYNihBKC96PhMz9yYx+/21FpkVfp2m1XB1gVQ+lrBKgpgtzw/hiSoNE6g4Pr3zRZ/4QBRm7qqtGCDELkIcSdXeInv1Rg6tHPWypQwDDB2d1sqHN73n/6aIjStDfR2vackVw8sXEr7YNWwj16WsekxicaIetcKhxCyMeI63hsSDLU39vbo9t1+0zkWVJkjNdk45Mwtq+ATQSeGDBy9/8OYabU+UIq4Pj5EnXWl86AvmYTHzd4qSGs9Qk6uGFjCUBC6ngdM2xpJdGft43yPH5fBurPL14fwKEKek4I7HEYEZxs7H8w+9GXpc+wAVcJw=~-1~-1~-1; defaultLang=en; nsit=y-ACHu09LRyawLlR24cChBdc; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTcxNTk0MTYyOCwiZXhwIjoxNzE1OTQ4ODI4fQ.GEJPuE4WlCIgg9wxiT0FeIxO4f2KOVO5az92MDUf3VE; bm_sz=68D4F180B377BE746D6D2CEE71BA4FDC~YAAQUGDQF1EfsIWPAQAAOVwXhhdLy80S3UkwMlVaQt8Dl6lBUpk/LA+R7U3sj6tcDOBuso6Y0T4lbfpvBuBYMwAdrxFiQ0CFxkATJuCi9Xxp2wkKBIjhNkaTJsmK+POz1AzVl62aDrKanXEXEfMsEM/b+gZYKbgWtruWc2KHlDxM6DnlDkYcsXSTDEgcN4c+U20KORlE61BNGvVjik7I9xMRwEyY250lwQNfEBG8woUrE1VkD1gnHJw0mSUY23HgMSKTEgcEYe5Ry55yV1bTqig8AblI0sMXmyJBCyqewBazc7wjG0KXpXyAd4idtHF1TNtJJil5aNjBzhXhG/md+w0b7F2XyOCIevjZJwp3ibTM793Wtv+4atdOOfdwLo8qMT9t8AlhzlcWfoYMgsI6A+2BYT9ZV7LmNeGdemFnvQ9Pqinu1e+hNMCv/fUISA==~3294513~3422531; ak_bmsc=E92B6BC7E9A337D1CB35F73B29B38208~000000000000000000000000000000~YAAQUGDQF8wfsIWPAQAA/GMXhheq0P4kGRUqJf34mf0Vd3o3ozNuREeACT6p0Q5151OJRucPRzYB0+NjZQMuTnyDeXYQZj02/YKizMeSzMq26z7M0tQweg3MfxO8zNTpZB0DxJCJ19m2mltS5nl7DUeOiXaM+QX/FDB3Z6zYJm3Ocu3VKFCg+VXapnGaVY875ZNfdl4nNqW0gn/3b3E26UKJzgH9VHkktYFqsSmCLrw4zBkgdfkVxH56TAEwhUQ1xBaloIMuLY2EIOgWIPaVfKxs/eGEWpA+U2wJVuEk7Vb03DESz/u1Y9oo55DYCyZ9Gfv1TjzLjSqaN7YqSBRG03yosg80Y2rMXaPrNyRwfNBEt4uzuvA94LSgLBeoe29b6ML8sFepK75K/Gm9M4a0cs+0n/5Ha8NeRFok6xnwCB50vQu3HvLYBbjA4SbWRhfwB4+KrebBBq5EBTf9SCI=; RT="z=1&dm=nseindia.com&si=a746dd1a-fbf2-473e-a100-db75208eb944&ss=lwajc7sy&sl=1&se=8c&tt=4oh&bcn=%2F%2F17de4c1d.akstat.io%2F&ld=5hh&nu=kpaxjfo&cl=82y"; _ga_QJZ4447QD3=GS1.1.1715941635.14.0.1715941635.0.0.0; _ga_87M7PJ3R97=GS1.1.1715941629.17.1.1715941635.0.0.0; bm_sv=017FEA61B10A4C271F845F44DA3EB05D~YAAQUGDQFzohsIWPAQAA4H0Xhhdz3tnBQL6DXJGCeRsxPifnKWrTRtB05DFN3oOX3K7DJvjb+5DDSnR67LnXNitTQczsXVKUjwm/Za/S5VMB5p5cCUyzqfzRPQQ+hS3PjiEt9fZE/9eRLu5kleETU8oR2fn3yMqJ9ohvUgCpPbhqEpb+vfUDoe0k4ksyuiredt9ORHbDvllqcjjmsiFeby5vbi2a863OmKr8XZwU3JK00Hiy3SaX0cBj/ThRuc6PHMw=~1'
                      }
            session = requests.Session()
            data = session.get(url, headers=headers).json()["records"]["data"]
            ocdata = []
            for i in data:
                for j, k in i.items():
                    if j == "CE" or j == "PE":
                        info = k
                        info["instrumentType"] = j
                        ocdata.append(info)

            df = pd.DataFrame(ocdata)
            # wb = xw.Book("optionchaintracker.xlsx")
            # st = wb.sheets("vedl")
            # st.range("A1").value = df
            # print(df)




            strikes = df.strikePrice.unique().tolist()
            strike_size = int(strikes[int(len(strikes) / 2) + 1]) - int(strikes[int(len(strikes) / 2)])






            for price in current_market_price(ticker, exchange):
                two_percent_cmp = price + 0.02 * price
                TWO_PERCENT_MARKET_PRICE = two_percent_cmp
                break

            print(TWO_PERCENT_MARKET_PRICE)

            # access dataframe for atm price
            atm = int(round(TWO_PERCENT_MARKET_PRICE / strike_size, 0) * strike_size)
            print(atm)

            output_ce = pd.DataFrame()

            atm_pe = atm
            output_pe = pd.DataFrame()

            for _ in range(5):

                # (for ce)
                ab = True
                while ab:

                    fd = df[df['strikePrice'] == atm]

                    if fd.empty:
                        print("empty df ce", atm)
                        atm = atm + 0.5
                        if atm > strikes[-1]:
                            break
                    else:
                        ab = False

                # print(fd)

                # (for pe)
                ab_pe = True
                while ab_pe:

                    fd_pe = df[df['strikePrice'] == atm_pe]

                    if fd_pe.empty:
                        print("empty df pe", atm_pe)
                        atm_pe = atm_pe - 0.5
                    else:
                        ab_pe = False

                # print(fd_pe)

                # (for ce)convert expiry date in particular format
                fd = fd.reset_index()
                for i in range(len(fd)):
                    expiry_date_str = fd["expiryDate"].iloc[i]
                    temp_expiry = datetime.datetime.strptime(expiry_date_str, '%d-%b-%Y')
                    result_expiry = temp_expiry.strftime('%d-%m-%Y')
                    fd.at[i, "expiryDate"] = result_expiry
                # print(fd)
                # print(type(fd["expiryDate"].iloc[0]))

                # (for pe) convert expiry date in particular format
                fd_pe = fd_pe.reset_index()
                for i in range(len(fd_pe)):
                    expiry_date_str_pe = fd_pe["expiryDate"].iloc[i]
                    temp_expiry_pe = datetime.datetime.strptime(expiry_date_str_pe, '%d-%b-%Y')
                    result_expiry_pe = temp_expiry_pe.strftime('%d-%m-%Y')
                    fd_pe.at[i, "expiryDate"] = result_expiry_pe

                # (last thursday (CE))
                today_year = datetime.datetime.now().year
                today_month = datetime.datetime.now().month
                today_day = datetime.datetime.now().day
                l_thursday = last_thursday_version_2(today_year, today_month)

                # if today is within the last thursday, then we will take current month last thursday as an adjusted_expiry
                if today_day < l_thursday.day or today_day == l_thursday.day and today_month == l_thursday.month:
                    adjusted_expiry = last_thursday_version_2(today_year, today_month)
                    print("in first if")
                # if today is greater than last thursday, then we will take next month last thursday as an adjusted_expiry
                if today_day > l_thursday.day and today_month == l_thursday.month:
                    adjusted_expiry = last_thursday(today_year, today_month)
                    print("in second if")

                format = '%d-%m-%Y'
                adjusted_expiry = adjusted_expiry.strftime(format)
                # year, month, day = str(l_thursday.date()).split("-")
                # l_thursday = f"{day}-{month}-{year}"
                # print(l_thursday)
                # print(l_thursday.date())
                # print(str(l_thursday.date()))
                # print(type(l_thursday.date()))
                # print(type(str(l_thursday.date())))

                # (last thursday (PE))
                today_year_pe = datetime.datetime.now().year
                today_month_pe = datetime.datetime.now().month
                today_day_pe = datetime.datetime.now().day
                l_thursday_pe = last_thursday_version_2(today_year_pe, today_month_pe)

                # if today is within the last thursday, then we will take current month last thursday as an adjusted_expiry
                if today_day_pe < l_thursday_pe.day or today_day_pe == l_thursday_pe.day and today_month_pe == l_thursday_pe.month:
                    adjusted_expiry_pe = last_thursday_version_2(today_year_pe, today_month_pe)
                    print("in first if")
                # if today is greater than last thursday, then we will take next month last thursday as an adjusted_expiry
                if today_day_pe > l_thursday_pe.day and today_month_pe == l_thursday_pe.month:
                    adjusted_expiry_pe = last_thursday(today_year_pe, today_month_pe)
                    print("in second if")

                format = '%d-%m-%Y'
                adjusted_expiry_pe = adjusted_expiry_pe.strftime(format)
                # year_pe, month_pe, day_pe = str(l_thursday_pe.date()).split("-")
                # l_thursday_pe = f"{day_pe}-{month_pe}-{year_pe}"

                # (subset_ce (CE))
                subset_ce = fd[(fd.instrumentType == "CE") & (fd.expiryDate == adjusted_expiry)]
                # print(subset_ce)
                output_ce = pd.concat([output_ce, subset_ce])

                # (subset_pe (PE))
                subset_pe = fd_pe[(fd_pe.instrumentType == "PE") & (fd_pe.expiryDate == adjusted_expiry_pe)]
                # print(subset_pe)
                output_pe = pd.concat([output_pe, subset_pe])

                # (for CE)
                atm += strike_size

                # (for PE)
                atm_pe -= strike_size

            output_ce = output_ce[["strikePrice", "expiryDate", "lastPrice", "instrumentType", "underlying"]]
            output_pe = output_pe[["strikePrice", "expiryDate", "lastPrice", "instrumentType", "underlying"]]

            output_ce.reset_index(drop=True, inplace=True)
            output_pe.reset_index(drop=True, inplace=True)

            return output_ce, output_pe

        except Exception as e:
            pass


# output_ce, output_pe = get_dataframe()
# print(output_ce)
# print(output_pe)

@st.experimental_fragment
def frag_table(table_number):
    shares = pd.read_csv("FNO Stocks - All FO Stocks List, Technical Analysis Scanner.csv")
    share_list = list(shares["Symbol"])
    selected_option = st.selectbox("Share List", share_list, key="share_list"+str(table_number))

    if selected_option in share_list:
        ticker = selected_option
        output_ce, output_pe = get_dataframe(ticker)

        ########################################## Stock LTP and Matrix #######################################
        stock_ltp = 0.0
        for price in current_market_price(ticker, exchange):
            stock_ltp = price
            break


        # ********************************** MATRIX ******************************************
        l1, l2 = len(output_ce), len(output_pe)
        if l1 < l2:
            fin_len = l1
        else:
            fin_len = l2
        matrix = np.zeros((fin_len, 4))
        df = pd.DataFrame(matrix, columns=["Call Ratio", "Call Effective Ratio", "Put Ratio", "Put Effective Ratio"])

        for i in range(len(df)):
            df.at[i, "Call Ratio"] = (output_ce["lastPrice"].iloc[i] / stock_ltp) * 100
            df.at[i, "Call Effective Ratio"] = (((output_ce["strikePrice"].iloc[i] - stock_ltp) + output_ce["lastPrice"].iloc[i]) / stock_ltp) * 100
            df.at[i, "Put Ratio"] = (output_pe["lastPrice"].iloc[i] / stock_ltp) * 100
            df.at[i, "Put Effective Ratio"] = (((stock_ltp - output_pe["strikePrice"].iloc[i]) + output_pe["lastPrice"].iloc[i]) / stock_ltp) * 100

        # ************************************************************************************
        col1, col2, col3 = st.columns(3)

        with col1:
            output_ce = output_ce.style.set_properties(**{'background-color':'palegreen'})
            st.dataframe(output_ce)
        with col2:
            output_pe = output_pe.style.set_properties(**{'background-color': 'antiquewhite'})
            st.dataframe(output_pe)
        with col3:
            df = df.style.set_properties(**{'background-color': 'paleturquoise'})
            st.dataframe(df)

        st.write(f'{ticker} LTP:', stock_ltp)


frag_table(1)
frag_table(2)
frag_table(3)
#*************************************************ONE******************************************************

#
# shares_1 = pd.read_csv("FNO Stocks - All FO Stocks List, Technical Analysis Scanner.csv")
# share_list_1 = list(shares_1["Symbol"])
# selected_option_1 = st.selectbox("Share List", share_list_1, key = "share_list_1")
#
# if selected_option_1 in share_list_1:
#     ticker_1 = selected_option_1
#     output_ce_1, output_pe_1 = get_dataframe(ticker_1)
#
#     ########################################## Stock LTP and Matrix #######################################
#     stock_ltp_1 = 0.0
#     for price in current_market_price(ticker_1, exchange):
#         stock_ltp_1 = price
#         break
#
#
#     # ********************************** MATRIX ******************************************
#     l1_1, l2_1 = len(output_ce_1), len(output_pe_1)
#     if l1_1 < l2_1:
#         fin_len_1 = l1_1
#     else:
#         fin_len_1 = l2_1
#     matrix_1 = np.zeros((fin_len_1, 4))
#     df_1 = pd.DataFrame(matrix_1, columns=["Call Ratio", "Call Effective Ratio", "Put Ratio", "Put Effective Ratio"])
#
#     for i in range(len(df_1)):
#         df_1.at[i, "Call Ratio"] = (output_ce_1["lastPrice"].iloc[i] / stock_ltp_1) * 100
#         df_1.at[i, "Call Effective Ratio"] = (((output_ce_1["strikePrice"].iloc[i] - stock_ltp_1) + output_ce_1["lastPrice"].iloc[i]) / stock_ltp_1) * 100
#         df_1.at[i, "Put Ratio"] = (output_pe_1["lastPrice"].iloc[i] / stock_ltp_1) * 100
#         df_1.at[i, "Put Effective Ratio"] = (((stock_ltp_1 - output_pe_1["strikePrice"].iloc[i]) + output_pe_1["lastPrice"].iloc[i]) / stock_ltp_1) * 100
#
#     # ************************************************************************************
#
#     col1_1, col2_1, col3_1 = st.columns(3)
#
#     with col1_1:
#         output_ce_1 = output_ce_1.style.set_properties(**{'background-color': 'palegreen'})
#         st.dataframe(output_ce_1)
#     with col2_1:
#         output_pe_1 = output_pe_1.style.set_properties(**{'background-color': 'antiquewhite'})
#         st.dataframe(output_pe_1)
#     with col3_1:
#         df_1 = df_1.style.set_properties(**{'background-color': 'paleturquoise'})
#         st.dataframe(df_1)
#
#     st.write(f'{ticker_1} LTP:', stock_ltp_1)
#
#
#
#
#
# #*************************************************TWO*********************************************
#
# shares_2 = pd.read_csv("FNO Stocks - All FO Stocks List, Technical Analysis Scanner.csv")
# share_list_2 = list(shares_2["Symbol"])
# selected_option_2 = st.selectbox("Share List", share_list_2, key = "share_list_2")
#
# if selected_option_2 in share_list_2:
#     ticker_2 = selected_option_2
#     output_ce_2, output_pe_2 = get_dataframe(ticker_2)
#
#     ########################################## Stock LTP and Matrix #######################################
#     stock_ltp_2 = 0.0
#     for price in current_market_price(ticker_2, exchange):
#         stock_ltp_2 = price
#         break
#
#
#     # ********************************** MATRIX ******************************************
#     l1_2, l2_2 = len(output_ce_2), len(output_pe_2)
#     if l1_2 < l2_2:
#         fin_len_2 = l1_2
#     else:
#         fin_len_2 = l2_2
#     matrix_2 = np.zeros((fin_len_2, 4))
#     df_2 = pd.DataFrame(matrix_2, columns=["Call Ratio", "Call Effective Ratio", "Put Ratio", "Put Effective Ratio"])
#
#     for i in range(len(df_2)):
#         df_2.at[i, "Call Ratio"] = (output_ce_2["lastPrice"].iloc[i] / stock_ltp_2) * 100
#         df_2.at[i, "Call Effective Ratio"] = (((output_ce_2["strikePrice"].iloc[i] - stock_ltp_2) + output_ce_2["lastPrice"].iloc[i]) / stock_ltp_2) * 100
#         df_2.at[i, "Put Ratio"] = (output_pe_2["lastPrice"].iloc[i] / stock_ltp_2) * 100
#         df_2.at[i, "Put Effective Ratio"] = (((stock_ltp_2 - output_pe_2["strikePrice"].iloc[i]) + output_pe_2["lastPrice"].iloc[i]) / stock_ltp_2) * 100
#
#     # ************************************************************************************
#     col1_2, col2_2, col3_2 = st.columns(3)
#
#     with col1_2:
#         output_ce_2 = output_ce_2.style.set_properties(**{'background-color': 'palegreen'})
#         st.dataframe(output_ce_2)
#     with col2_2:
#         output_pe_2 = output_pe_2.style.set_properties(**{'background-color': 'antiquewhite'})
#         st.dataframe(output_pe_2)
#     with col3_2:
#         df_2 = df_2.style.set_properties(**{'background-color': 'paleturquoise'})
#         st.dataframe(df_2)
#
#     st.write(f'{ticker_2} LTP:', stock_ltp_2)
#
