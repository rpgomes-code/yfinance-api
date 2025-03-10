from fastapi import FastAPI
import yfinance as yf

from utils.yfinance_data_manager import clean_yfinance_data

app = FastAPI()

# Ticker Endpoints (Exemple value to use: AAPL)

@app.get("/v1/ticker/{ticker}/actions")
@clean_yfinance_data
async def get_ticker_actions(ticker: str):
    return yf.Ticker(ticker).actions

@app.get("/v1/ticker/{ticker}/analyst-price-targets")
@clean_yfinance_data
async def get_ticker_analyst_price_targets(ticker: str):
    return yf.Ticker(ticker).analyst_price_targets

@app.get("/v1/ticker/{ticker}/balance-sheet")
@clean_yfinance_data
async def get_ticker_balance_sheet(ticker: str):
    return yf.Ticker(ticker).balance_sheet

@app.get("/v1/ticker/{ticker}/balancesheet")
@clean_yfinance_data
async def get_ticker_balancesheet(ticker: str):
    return yf.Ticker(ticker).balancesheet

@app.get("/v1/ticker/{ticker}/basic-info")
@clean_yfinance_data
async def get_ticker_basic_info(ticker: str):
    return yf.Ticker(ticker).basic_info

@app.get("/v1/ticker/{ticker}/calendar")
@clean_yfinance_data
async def get_ticker_calendar(ticker: str):
    return yf.Ticker(ticker).calendar

@app.get("/v1/ticker/{ticker}/capital-gains") # Function is returning an empty dictionary
@clean_yfinance_data
async def get_ticker_capital_gains(ticker: str):
    return yf.Ticker(ticker).capital_gains

@app.get("/v1/ticker/{ticker}/cash-flow")
@clean_yfinance_data
async def get_ticker_cash_flow(ticker: str):
    return yf.Ticker(ticker).cash_flow

@app.get("/v1/ticker/{ticker}/cashflow")
@clean_yfinance_data
async def get_ticker_cashflow(ticker: str):
    return yf.Ticker(ticker).cashflow

@app.get("/v1/ticker/{ticker}/dividends")
@clean_yfinance_data
async def get_ticker_dividends(ticker: str):
    return yf.Ticker(ticker).dividends

@app.get("/v1/ticker/{ticker}/earnings") # Function is returning null
@clean_yfinance_data
async def get_ticker_earnings(ticker: str):
    return yf.Ticker(ticker).earnings

@app.get("/v1/ticker/{ticker}/earnings-dates")
@clean_yfinance_data
async def get_ticker_earnings_dates(ticker: str):
    return yf.Ticker(ticker).earnings_dates

@app.get("/v1/ticker/{ticker}/earnings-estimate")
@clean_yfinance_data
async def get_ticker_earnings_estimate(ticker: str):
    return yf.Ticker(ticker).earnings_estimate

@app.get("/v1/ticker/{ticker}/earnings-history")
@clean_yfinance_data
async def get_ticker_earnings_history(ticker: str):
    return yf.Ticker(ticker).earnings_history

@app.get("/v1/ticker/{ticker}/eps-revisions")
@clean_yfinance_data
async def get_ticker_eps_revisions(ticker: str):
    return yf.Ticker(ticker).eps_revisions

@app.get("/v1/ticker/{ticker}/eps-trend")
@clean_yfinance_data
async def get_ticker_eps_trend(ticker: str):
    return yf.Ticker(ticker).eps_trend

@app.get("/v1/ticker/{ticker}/fast-info")
@clean_yfinance_data
async def get_ticker_fast_info(ticker: str):
    return yf.Ticker(ticker).fast_info

@app.get("/v1/ticker/{ticker}/financials")
@clean_yfinance_data
async def get_ticker_financials(ticker: str):
    return yf.Ticker(ticker).financials

@app.get("/v1/ticker/{ticker}/funds-data") # Some error is happening here needs to be fixed
@clean_yfinance_data
async def get_ticker_funds_data(ticker: str):
    return yf.Ticker(ticker).funds_data

@app.get("/v1/ticker/{ticker}/growth-estimates")
@clean_yfinance_data
async def get_ticker_growth_estimates(ticker: str):
    return yf.Ticker(ticker).growth_estimates

@app.get("/v1/ticker/{ticker}/history-metadata")
@clean_yfinance_data
async def get_ticker_history_metadata(ticker: str):
    return yf.Ticker(ticker).history_metadata

@app.get("/v1/ticker/{ticker}/income-stmt")
@clean_yfinance_data
async def get_ticker_income_stmt(ticker: str):
    return yf.Ticker(ticker).income_stmt

@app.get("/v1/ticker/{ticker}/incomestmt")
@clean_yfinance_data
async def get_ticker_incomestmt(ticker: str):
    return yf.Ticker(ticker).incomestmt

@app.get("/v1/ticker/{ticker}/info")
@clean_yfinance_data
async def get_ticker_info(ticker: str):
    return yf.Ticker(ticker).info

@app.get("/v1/ticker/{ticker}/insider-purchases")
@clean_yfinance_data
async def get_ticker_insider_purchases(ticker: str):
    return yf.Ticker(ticker).insider_purchases

@app.get("/v1/ticker/{ticker}/insider-roster-holders")
@clean_yfinance_data
async def get_ticker_insider_roster_holders(ticker: str):
    return yf.Ticker(ticker).insider_roster_holders

@app.get("/v1/ticker/{ticker}/insider-transactions")
@clean_yfinance_data
async def get_ticker_insider_transactions(ticker: str):
    return yf.Ticker(ticker).insider_transactions

@app.get("/v1/ticker/{ticker}/institutional-holders")
@clean_yfinance_data
async def get_ticker_institutional_holders(ticker: str):
    return yf.Ticker(ticker).institutional_holders

@app.get("/v1/ticker/{ticker}/isin")
@clean_yfinance_data
async def get_ticker_isin(ticker: str):
    return yf.Ticker(ticker).isin

@app.get("/v1/ticker/{ticker}/major-holders")
@clean_yfinance_data
async def get_ticker_major_holders(ticker: str):
    return yf.Ticker(ticker).major_holders

@app.get("/v1/ticker/{ticker}/mutualfund-holders")
@clean_yfinance_data
async def get_ticker_mutualfund_holders(ticker: str):
    return yf.Ticker(ticker).mutualfund_holders

@app.get("/v1/ticker/{ticker}/news")
@clean_yfinance_data
async def get_ticker_news(ticker: str):
    return yf.Ticker(ticker).news

@app.get("/v1/ticker/{ticker}/options")
@clean_yfinance_data
async def get_ticker_options(ticker: str):
    return yf.Ticker(ticker).options

@app.get("/v1/ticker/{ticker}/quarterly-balance-sheet")
@clean_yfinance_data
async def get_ticker_quarterly_balance_sheet(ticker: str):
    return yf.Ticker(ticker).quarterly_balance_sheet

@app.get("/v1/ticker/{ticker}/quarterly-balancesheet")
@clean_yfinance_data
async def get_ticker_quarterly_balancesheet(ticker: str):
    return yf.Ticker(ticker).quarterly_balancesheet

@app.get("/v1/ticker/{ticker}/quarterly-cash-flow")
@clean_yfinance_data
async def get_ticker_quarterly_cash_flow(ticker: str):
    return yf.Ticker(ticker).quarterly_cash_flow

@app.get("/v1/ticker/{ticker}/quarterly-cashflow")
@clean_yfinance_data
async def get_ticker_quarterly_cashflow(ticker: str):
    return yf.Ticker(ticker).quarterly_cashflow

@app.get("/v1/ticker/{ticker}/quarterly-earnings") # Function is returning null
@clean_yfinance_data
async def get_ticker_quarterly_earnings(ticker: str):
    return yf.Ticker(ticker).quarterly_earnings

@app.get("/v1/ticker/{ticker}/quarterly-financials")
@clean_yfinance_data
async def get_ticker_quarterly_financials(ticker: str):
    return yf.Ticker(ticker).quarterly_financials

@app.get("/v1/ticker/{ticker}/quarterly-income-stmt")
@clean_yfinance_data
async def get_ticker_quarterly_income_stmt(ticker: str):
    return yf.Ticker(ticker).quarterly_income_stmt

@app.get("/v1/ticker/{ticker}/quarterly-incomestmt")
@clean_yfinance_data
async def get_ticker_quarterly_incomestmt(ticker: str):
    return yf.Ticker(ticker).quarterly_incomestmt

@app.get("/v1/ticker/{ticker}/recommendations")
@clean_yfinance_data
async def get_ticker_recommendations(ticker: str):
    return yf.Ticker(ticker).recommendations

@app.get("/v1/ticker/{ticker}/recommendations-summary")
@clean_yfinance_data
async def get_ticker_recommendations_summary(ticker: str):
    return yf.Ticker(ticker).recommendations_summary

@app.get("/v1/ticker/{ticker}/revenue-estimate")
@clean_yfinance_data
async def get_ticker_revenue_estimate(ticker: str):
    return yf.Ticker(ticker).revenue_estimate

@app.get("/v1/ticker/{ticker}/sec-filings")
@clean_yfinance_data
async def get_ticker_sec_filings(ticker: str):
    return yf.Ticker(ticker).sec_filings

@app.get("/v1/ticker/{ticker}/shares") # Some error is happening here needs to be fixed
@clean_yfinance_data
async def get_ticker_shares(ticker: str):
    return yf.Ticker(ticker).shares

@app.get("/v1/ticker/{ticker}/splits")
@clean_yfinance_data
async def get_ticker_splits(ticker: str):
    return yf.Ticker(ticker).splits

@app.get("/v1/ticker/{ticker}/sustainability")
@clean_yfinance_data
async def get_ticker_sustainability(ticker: str):
    return yf.Ticker(ticker).sustainability

@app.get("/v1/ticker/{ticker}/upgrades-downgrades")
@clean_yfinance_data
async def get_ticker_upgrades_downgrades(ticker: str):
    return yf.Ticker(ticker).upgrades_downgrades

# Market Endpoints (Exemple value to use: US)

@app.get("/v1/market/{market}/status")
@clean_yfinance_data
async def get_market_status(market: str):
    return yf.Market(market).status

@app.get("/v1/market/{market}/summary")
@clean_yfinance_data
async def get_market_summary(market: str):
    return yf.Market(market).summary

# Search Endpoints (Exemple value to use: AAPL)

@app.get("/v1/search/{query}/all")
@clean_yfinance_data
async def search_all(query: str):
    return yf.Search(query).all

@app.get("/v1/search/{query}/lists") # Function is returning an empty dictionary
@clean_yfinance_data
async def search_lists(query: str):
    return yf.Search(query).lists

@app.get("/v1/search/{query}/news")
@clean_yfinance_data
async def search_news(query: str):
    return yf.Search(query).news

@app.get("/v1/search/{query}/quotes")
@clean_yfinance_data
async def search_quotes(query: str):
    return yf.Search(query).quotes

@app.get("/v1/search/{query}/research") # Function is returning an empty dictionary
@clean_yfinance_data
async def search_research(query: str):
    return yf.Search(query).research

@app.get("/v1/search/{query}/response")
@clean_yfinance_data
async def search_response(query: str):
    return yf.Search(query).response

# Sector Endpoints (Exemple value to use: energy)

@app.get("/v1/sector/{sector}/industries")
@clean_yfinance_data
async def get_sector_industries(sector: str):
    return yf.Sector(sector).industries

@app.get("/v1/sector/{sector}/key")
@clean_yfinance_data
async def get_sector_key(sector: str):
    return yf.Sector(sector).key

@app.get("/v1/sector/{sector}/name")
@clean_yfinance_data
async def get_sector_name(sector: str):
    return yf.Sector(sector).name

@app.get("/v1/sector/{sector}/overview")
@clean_yfinance_data
async def get_sector_overview(sector: str):
    return yf.Sector(sector).overview

@app.get("/v1/sector/{sector}/research-reports")
@clean_yfinance_data
async def get_sector_research_reports(sector: str):
    return yf.Sector(sector).research_reports

@app.get("/v1/sector/{sector}/symbol")
@clean_yfinance_data
async def get_sector_symbol(sector: str):
    return yf.Sector(sector).symbol

@app.get("/v1/sector/{sector}/ticker") # Some error is happening here needs to be fixed
@clean_yfinance_data
async def get_sector_ticker(sector: str):
    return yf.Sector(sector).ticker

@app.get("/v1/sector/{sector}/top-companies")
@clean_yfinance_data
async def get_sector_top_companies(sector: str):
    return yf.Sector(sector).top_companies

@app.get("/v1/sector/{sector}/top-etfs")
@clean_yfinance_data
async def get_sector_top_etfs(sector: str):
    return yf.Sector(sector).top_etfs

@app.get("/v1/sector/{sector}/top-mutual-funds")
@clean_yfinance_data
async def get_sector_top_mutual_funds(sector: str):
    return yf.Sector(sector).top_mutual_funds

# Industry Endpoints (Exemple value to use: gold)

@app.get("/v1/industry/{industry}/key")
@clean_yfinance_data
async def get_industry_key(industry: str):
    return yf.Industry(industry).key

@app.get("/v1/industry/{industry}/name")
@clean_yfinance_data
async def get_industry_name(industry: str):
    return yf.Industry(industry).name

@app.get("/v1/industry/{industry}/overview")
@clean_yfinance_data
async def get_industry_overview(industry: str):
    return yf.Industry(industry).overview

@app.get("/v1/industry/{industry}/research-reports")
@clean_yfinance_data
async def get_industry_research_reports(industry: str):
    return yf.Industry(industry).research_reports

@app.get("/v1/industry/{industry}/sector-key")
@clean_yfinance_data
async def get_industry_sector_key(industry: str):
    return yf.Industry(industry).sector_key

@app.get("/v1/industry/{industry}/sector-name")
@clean_yfinance_data
async def get_industry_sector_name(industry: str):
    return yf.Industry(industry).sector_name

@app.get("/v1/industry/{industry}/symbol")
@clean_yfinance_data
async def get_industry_symbol(industry: str):
    return yf.Industry(industry).symbol

@app.get("/v1/industry/{industry}/ticker") # Some error is happening here needs to be fixed
@clean_yfinance_data
async def get_industry_ticker(industry: str):
    return yf.Industry(industry).ticker

@app.get("/v1/industry/{industry}/top-companies")
@clean_yfinance_data
async def get_industry_top_companies(industry: str):
    return yf.Industry(industry).top_companies

@app.get("/v1/industry/{industry}/top-growth-companies")
@clean_yfinance_data
async def get_industry_top_growth_companies(industry: str):
    return yf.Industry(industry).top_growth_companies

@app.get("/v1/industry/{industry}/top-performing-companies")
@clean_yfinance_data
async def get_industry_top_performing_companies(industry: str):
    return yf.Industry(industry).top_performing_companies

@app.get("/v1/industry/{industry}/overview")
@clean_yfinance_data
async def get_industry_overview(industry: str):
    return yf.Industry(industry).overview