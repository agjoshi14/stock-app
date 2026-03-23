import streamlit as st
import pandas as pd
import yfinance as yf
from textblob import TextBlob
import requests
from streamlit import column_config

st.set_page_config(layout="wide")

# NASDAQ-100 companies
TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "NFLX",
    "TSLA", "GOOGL", "GOOG", "META", "AVGO",
    "PLTR", "CDNS", "ADBE", "CSCO", "CMCSA",
    "COST", "CRWD", "AMD", "AMAT", "ASML",
    "ATVI", "BIIB", "BKNG", "CHTR", "CPRT",
    "CTSH", "DXCM", "DDOG", "FANG", "GILD",
    "HON", "ILMN", "INTC", "INTU", "JD",
    "KLAC", "LLY", "LRCX", "LULU", "MAR",
    "MRNA", "MRVL", "MU", "NAVI", "ODFL",
    "ORLY", "PCAR", "PSTG", "PAYX", "REGN",
    "ROST", "SIRI", "SNPS", "TEAM", "TCOM",
    "TSMC", "TTD", "VRSN", "VRSK", "VRTX",
    "WDAY", "XEL", "ZM", "ZS", "DECK"
]

# Company name mapping
COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "NVDA": "NVIDIA Corp.",
    "AMZN": "Amazon.com Inc.",
    "NFLX": "Netflix Inc.",
    "TSLA": "Tesla Inc.",
    "GOOGL": "Alphabet Inc. (Class A)",
    "GOOG": "Alphabet Inc. (Class C)",
    "META": "Meta Platforms Inc.",
    "AVGO": "Broadcom Inc.",
    "PLTR": "Palantir Technologies",
    "CDNS": "Cadence Design Systems",
    "ADBE": "Adobe Inc.",
    "CSCO": "Cisco Systems Inc.",
    "CMCSA": "Comcast Corp.",
    "COST": "Costco Wholesale",
    "CRWD": "CrowdStrike Holdings",
    "AMD": "Advanced Micro Devices",
    "AMAT": "Applied Materials",
    "ASML": "ASML Holding",
    "ATVI": "Activision Blizzard",
    "BIIB": "Biogen Inc.",
    "BKNG": "Booking.com Inc.",
    "CHTR": "Charter Communications",
    "CPRT": "Carpetright PLC",
    "CTSH": "Cognizant Technology",
    "DXCM": "DexCom Inc.",
    "DDOG": "Datadog Inc.",
    "FANG": "Diamondback Energy",
    "GILD": "Gilead Sciences",
    "HON": "Honeywell International",
    "ILMN": "Illumina Inc.",
    "INTC": "Intel Corp.",
    "INTU": "Intuit Inc.",
    "JD": "JD.com Inc.",
    "KLAC": "KLA Corp.",
    "LLY": "Eli Lilly & Co.",
    "LRCX": "Lam Research",
    "LULU": "Lululemon Athletica",
    "MAR": "Marriott International",
    "MRNA": "Moderna Inc.",
    "MRVL": "Marvell Technology",
    "MU": "Micron Technology",
    "NAVI": "Navient Corp.",
    "ODFL": "Old Dominion Freight",
    "ORLY": "O'Reilly Automotive",
    "PCAR": "PACCAR Inc.",
    "PSTG": "Pure Storage Inc.",
    "PAYX": "Paychex Inc.",
    "REGN": "Regeneron Pharma",
    "ROST": "Ross Stores Inc.",
    "SIRI": "Sirius XM Holdings",
    "SNPS": "Synopsys Inc.",
    "TEAM": "Atlassian Corp.",
    "TCOM": "Trip.com Group",
    "TSMC": "Taiwan Semiconductor",
    "TTD": "The Trade Desk",
    "VRSN": "VeriSign Inc.",
    "VRSK": "Verisk Analytics",
    "VRTX": "Vertex Pharmaceuticals",
    "WDAY": "Workday Inc.",
    "XEL": "Xcel Energy",
    "ZM": "Zoom Video Communications",
    "ZS": "Zscaler Inc.",
    "DECK": "Deckers Outdoor Corp."
}

# -------------------------------
# FUNCTIONS
# -------------------------------

def get_price(ticker):
   try:
       stock = yf.Ticker(ticker)
       data = stock.history(period="1d")
       if data.empty:
           return None
       return round(data["Close"].iloc[-1], 2)
   except:
       return None

def get_financials(ticker):
   stock = yf.Ticker(ticker)
   fin = stock.quarterly_financials

   try:
       revenue = fin.loc["Total Revenue"]
       current = revenue.iloc[0]
       prev_q = revenue.iloc[1]
       prev_y = revenue.iloc[4]

       yoy = (current - prev_y) / prev_y * 100
       qoq = (current - prev_q) / prev_q * 100

       return round(yoy, 2), round(qoq, 2)
   except:
       return None, None

# Mock news data for NASDAQ-100 companies
MOCK_NEWS = {
    "AAPL": {
        "news": "Apple Q1 earnings beat estimates with strong iPhone sales and services growth. Revenue increased 4.2% YoY despite market challenges.",
        "url": "https://www.reuters.com/apple",
        "sentiment": "Positive"
    },
    "MSFT": {
        "news": "Microsoft Azure cloud revenue grows 29% driven by AI and enterprise demand. Strong guidance for Q2 announced.",
        "url": "https://www.cnbc.com/microsoft",
        "sentiment": "Positive"
    },
    "NVDA": {
        "news": "NVIDIA H100 chips face shortage as demand for AI accelerators remains high. Future guidance exceeds expectations.",
        "url": "https://www.bloomberg.com/nvdia",
        "sentiment": "Positive"
    },
    "AMZN": {
        "news": "Amazon Web Services reaches record revenue with 24% growth. Cloud division outperforms expectations.",
        "url": "https://www.reuters.com/amazon",
        "sentiment": "Positive"
    },
    "NFLX": {
        "news": "Netflix subscriber growth slows as competition intensifies. Ad tier adoption accelerates but pricing concerns remain.",
        "url": "https://www.cnbc.com/netflix",
        "sentiment": "Neutral"
    },
    "TSLA": {
        "news": "Tesla faces production challenges at Berlin and Austin factories. Q1 delivery targets may be missed.",
        "url": "https://www.bloomberg.com/tesla",
        "sentiment": "Negative"
    },
    "GOOGL": {
        "news": "Google announces strong advertising recovery and AI initiatives. Search dominance remains unchallenged.",
        "url": "https://www.reuters.com/google",
        "sentiment": "Positive"
    },
    "GOOG": {
        "news": "Google announces strong advertising recovery and AI initiatives. Search dominance remains unchallenged.",
        "url": "https://www.reuters.com/google",
        "sentiment": "Positive"
    },
    "META": {
        "news": "Meta's AI efficiency improvements boost profit margins. Reality Labs losses narrow as metaverse focus continues.",
        "url": "https://www.cnbc.com/meta",
        "sentiment": "Positive"
    },
    "AVGO": {
        "news": "Broadcom secures major chip orders from hyperscalers. Positioned well for AI infrastructure buildout.",
        "url": "https://www.bloomberg.com/broadcom",
        "sentiment": "Positive"
    },
    "PLTR": {
        "news": "Palantir stock surges on strong guidance and enterprise client growth. Commercial segment shows momentum.",
        "url": "https://www.reuters.com/palantir",
        "sentiment": "Positive"
    },
    "CDNS": {
        "news": "Cadence Design Systems reports mixed earnings. Chip design tools demand normalizes after strong cycle.",
        "url": "https://www.cnbc.com/cadence",
        "sentiment": "Neutral"
    },
    "ADBE": {
        "news": "Adobe's AI features drive strong subscription growth. Firefly integration boosts creative cloud adoption.",
        "url": "https://www.bloomberg.com/adobe",
        "sentiment": "Positive"
    },
    "CSCO": {
        "news": "Cisco misses earnings expectations as enterprise IT spending slows. Cost cutting initiated.",
        "url": "https://www.reuters.com/cisco",
        "sentiment": "Negative"
    },
    "CMCSA": {
        "news": "Comcast cable subscriber losses accelerate amid cord-cutting trends. Focus shifts to broadband growth.",
        "url": "https://www.cnbc.com/comcast",
        "sentiment": "Negative"
    },
    "COST": {
        "news": "Costco raises membership fees with strong warehouse traffic. Same-store sales exceed market expectations.",
        "url": "https://www.bloomberg.com/costco",
        "sentiment": "Positive"
    },
    "CRWD": {
        "news": "CrowdStrike wins major enterprise security contracts. Cybersecurity spending remains robust.",
        "url": "https://www.reuters.com/crowdstrike",
        "sentiment": "Positive"
    },
    "AMD": {
        "news": "AMD secures data center contracts beating Intel. AI processor roadmap accelerates.",
        "url": "https://www.cnbc.com/amd",
        "sentiment": "Positive"
    },
    "AMAT": {
        "news": "Applied Materials reports strong chip equipment orders. Semiconductor manufacturing capacity expands.",
        "url": "https://www.bloomberg.com/amat",
        "sentiment": "Positive"
    },
    "ASML": {
        "news": "ASML secures long-term supply contracts from chip makers. EUV lithography demand remains strong.",
        "url": "https://www.reuters.com/asml",
        "sentiment": "Positive"
    },
    "ATVI": {
        "news": "Activision Blizzard faces regulatory scrutiny in multiple jurisdictions. Employee retention improves.",
        "url": "https://www.cnbc.com/activision",
        "sentiment": "Negative"
    },
    "BIIB": {
        "news": "Biogen's Alzheimer's drug receives FDA approval. Commercial launch timeline clarified.",
        "url": "https://www.bloomberg.com/biogen",
        "sentiment": "Positive"
    },
    "BKNG": {
        "news": "Booking.com travel demand remains strong post-holiday. Margin expansion continues.",
        "url": "https://www.reuters.com/booking",
        "sentiment": "Positive"
    },
    "CHTR": {
        "news": "Charter Communications reports video subscriber losses offset by broadband growth.",
        "url": "https://www.cnbc.com/charter",
        "sentiment": "Neutral"
    },
    "CPRT": {
        "news": "Carpetright announces store closures as retail footprint shrinks. Online sales growing.",
        "url": "https://www.bloomberg.com/carpetright",
        "sentiment": "Negative"
    },
    "CTSH": {
        "news": "Cognizant Software Services wins major digital transformation deal. Tech spending improves.",
        "url": "https://www.reuters.com/cognizant",
        "sentiment": "Positive"
    },
    "DXCM": {
        "news": "DexCom diabetes monitoring device market share expands globally. Reimbursement environment improves.",
        "url": "https://www.cnbc.com/dexcom",
        "sentiment": "Positive"
    },
    "DDOG": {
        "news": "Datadog lands major enterprise cloud monitoring contracts. Platform adoption accelerates.",
        "url": "https://www.bloomberg.com/datadog",
        "sentiment": "Positive"
    },
    "FANG": {
        "news": "Diamondback Energy benefits from oil price recovery. Production guidance raised.",
        "url": "https://www.reuters.com/diamondback",
        "sentiment": "Positive"
    },
    "GILD": {
        "news": "Gilead Sciences gains new cancer treatment approvals. Pipeline momentum builds.",
        "url": "https://www.cnbc.com/gilead",
        "sentiment": "Positive"
    },
    "HON": {
        "news": "Honeywell strategic restructuring shows early results. Aerospace segment recovers well.",
        "url": "https://www.bloomberg.com/honeywell",
        "sentiment": "Positive"
    },
    "ILMN": {
        "news": "Illumina faces competition from Chinese gene sequencing firms. Market consolidation concerns rise.",
        "url": "https://www.reuters.com/illumina",
        "sentiment": "Negative"
    },
    "INTC": {
        "news": "Intel manufacturing expansion delayed amid budget constraints. Competitive pressures intensify.",
        "url": "https://www.cnbc.com/intel",
        "sentiment": "Negative"
    },
    "INTU": {
        "news": "Intuit software subscriptions grow double digits. Cloud platform adoption accelerates.",
        "url": "https://www.bloomberg.com/intuit",
        "sentiment": "Positive"
    },
    "JD": {
        "news": "JD.com Q4 earnings show recovery in Chinese online retail. Logistics network expansion continues.",
        "url": "https://www.reuters.com/jdcom",
        "sentiment": "Positive"
    },
    "KLAC": {
        "news": "KLA Corporation semiconductor inspection tools in strong demand. Process control market booming.",
        "url": "https://www.cnbc.com/kla",
        "sentiment": "Positive"
    },
    "LLY": {
        "news": "Eli Lilly's diabetes drug shows impressive phase 3 results. Blockbuster potential confirmed.",
        "url": "https://www.bloomberg.com/lilly",
        "sentiment": "Positive"
    },
    "LRCX": {
        "news": "Lam Research sees robust semiconductor equipment demand continuing. Margin expansion ongoing.",
        "url": "https://www.reuters.com/lamresearch",
        "sentiment": "Positive"
    },
    "LULU": {
        "news": "Lululemon posts strong athleisure demand. Expansion into male customer segment succeeds.",
        "url": "https://www.cnbc.com/lululemon",
        "sentiment": "Positive"
    },
    "MAR": {
        "news": "Marriott International benefits from luxury travel recovery. RevPAR metrics exceed expectations.",
        "url": "https://www.bloomberg.com/marriott",
        "sentiment": "Positive"
    },
    "MRNA": {
        "news": "Moderna vaccine pipeline expands with multiple RSV trials. Growth beyond COVID questioned.",
        "url": "https://www.reuters.com/moderna",
        "sentiment": "Neutral"
    },
    "MRVL": {
        "news": "Marvell Technology gains market share in data center chips. AI accelerator demand strong.",
        "url": "https://www.cnbc.com/marvell",
        "sentiment": "Positive"
    },
    "MU": {
        "news": "Micron Technology memory chip supply remains tight. Pricing holds firm amid demand.",
        "url": "https://www.bloomberg.com/micron",
        "sentiment": "Positive"
    },
    "NAVI": {
        "news": "Navient student loan servicer faces regulatory challenges. Profitability concerns mount.",
        "url": "https://www.reuters.com/navient",
        "sentiment": "Negative"
    },
    "ODFL": {
        "news": "Old Dominion Freight freight volumes recover strongly. Operating leverage improves.",
        "url": "https://www.cnbc.com/odfl",
        "sentiment": "Positive"
    },
    "ORLY": {
        "news": "O'Reilly Automotive same-store sales accelerate. DIY market momentum continues.",
        "url": "https://www.bloomberg.com/oreillyauto",
        "sentiment": "Positive"
    },
    "PCAR": {
        "news": "PACCAR truck orders surge on infrastructure spending. Backlog reaches record levels.",
        "url": "https://www.reuters.com/paccar",
        "sentiment": "Positive"
    },
    "PSTG": {
        "news": "Pure Storage storage solutions gain enterprise adoption. Subscription revenue accelerates.",
        "url": "https://www.cnbc.com/purestorage",
        "sentiment": "Positive"
    },
    "PAYX": {
        "news": "Paychex payroll processing business shows steady growth. Employee retention strong.",
        "url": "https://www.bloomberg.com/paychex",
        "sentiment": "Positive"
    },
    "REGN": {
        "news": "Regeneron obesity treatment shows strong clinical potential. Peak sales estimates rise.",
        "url": "https://www.reuters.com/regeneron",
        "sentiment": "Positive"
    },
    "ROST": {
        "news": "Ross Stores off-price retail strategy succeeds. Discount shopping demand robust.",
        "url": "https://www.cnbc.com/rossstores",
        "sentiment": "Positive"
    },
    "SIRI": {
        "news": "SiriusXM satellite radio subscriber trends stabilize. Marketing costs elevated.",
        "url": "https://www.bloomberg.com/siriusxm",
        "sentiment": "Neutral"
    },
    "SNPS": {
        "news": "Synopsys secures chip design tool contracts for advanced nodes. AI-powered EDA tools gain traction.",
        "url": "https://www.reuters.com/synopsys",
        "sentiment": "Positive"
    },
    "TEAM": {
        "news": "Atlassian cloud adoption accelerates across enterprise. DevOps market expanding rapidly.",
        "url": "https://www.cnbc.com/atlassian",
        "sentiment": "Positive"
    },
    "TCOM": {
        "news": "Trip.com China travel recovery drives booking surge. Regulatory environment stabilizes.",
        "url": "https://www.bloomberg.com/tripcom",
        "sentiment": "Positive"
    },
    "TSMC": {
        "news": "Taiwan Semiconductor Manufacturing reports record revenue. AI chip production capacity increases.",
        "url": "https://www.reuters.com/tsmc",
        "sentiment": "Positive"
    },
    "TTD": {
        "news": "The Trade Desk demand-side platform market share grows. Programmatic advertising boom continues.",
        "url": "https://www.cnbc.com/thetradedesk",
        "sentiment": "Positive"
    },
    "VRSN": {
        "news": "VeriSign domain name registry remains essential infrastructure. Pricing power holds.",
        "url": "https://www.bloomberg.com/verisign",
        "sentiment": "Positive"
    },
    "VRSK": {
        "news": "Verisk Analytics insurance data analytics sees strong demand. Digital transformation benefits accrue.",
        "url": "https://www.reuters.com/verisk",
        "sentiment": "Positive"
    },
    "VRTX": {
        "news": "Vertex Pharmaceuticals cystic fibrosis drug pipeline expands. Rare disease focus paying off.",
        "url": "https://www.cnbc.com/vertex",
        "sentiment": "Positive"
    },
    "WDAY": {
        "news": "Workday enterprise software cloud adoption accelerates. HR platform momentum builds.",
        "url": "https://www.bloomberg.com/workday",
        "sentiment": "Positive"
    },
    "XEL": {
        "news": "Xcel Energy renewable energy expansion on track. Utility regulation remains supportive.",
        "url": "https://www.reuters.com/xcelenergy",
        "sentiment": "Positive"
    },
    "ZM": {
        "news": "Zoom video conferencing faces intense competition. Enterprise deals remain strong.",
        "url": "https://www.cnbc.com/zoom",
        "sentiment": "Neutral"
    },
    "ZS": {
        "news": "Zscaler cloud security platform market leadership solidifies. Zero-trust architecture adoption accelerates.",
        "url": "https://www.bloomberg.com/zscaler",
        "sentiment": "Positive"
    },
    "DECK": {
        "news": "Deckers outdoor apparel brand expands internationally. Premium positioning strengthens.",
        "url": "https://www.reuters.com/deckers",
        "sentiment": "Positive"
    }
}

def get_news_sentiment(ticker):
   """Get latest news and sentiment for ticker - fetches dynamically from NewsAPI"""
   try:
       # Use company name for better search results instead of ticker symbol
       company_name = COMPANY_NAMES.get(ticker, ticker)
       
       # NewsAPI endpoint - using a free API key (replace with your own from newsapi.org)
       # Sign up at https://newsapi.org to get a free API key
       api_key = "d1d24710463f4fa595cf068e8c3c0636"  # Free public key for demo
       
       # Search using company name for more relevant results
       search_query = f"{company_name} stock earnings"
       url = f"https://newsapi.org/v2/everything?q={search_query}&sortBy=publishedAt&language=en&pageSize=1"
       
       # Add API key if available
       if api_key and api_key != "YOUR_API_KEY":
           url += f"&apiKey={api_key}"
       
       response = requests.get(url, timeout=5)
       
       if response.status_code == 200:
           data = response.json()
           articles = data.get("articles", [])
           
           if articles:
               article = articles[0]
               title = article.get("title", "")
               description = article.get("description", "")
               url_article = article.get("url", "")
               
               # Combine title and description for sentiment analysis
               text = f"{title} {description}"
               
               # Perform sentiment analysis
               blob = TextBlob(text)
               polarity = blob.sentiment.polarity
               
               # Summarize news
               news_summary = title if title else description
               if len(news_summary) > 150:
                   news_summary = news_summary[:150] + "..."
               
               # Determine sentiment
               if polarity > 0.1:
                   sentiment = "Positive"
                   sentiment_score = 0.7
               elif polarity < -0.1:
                   sentiment = "Negative"
                   sentiment_score = -0.7
               else:
                   sentiment = "Neutral"
                   sentiment_score = 0.0
               
               return sentiment, sentiment_score, news_summary, url_article
       
       # Fallback to mock data if API fails
       if ticker in MOCK_NEWS:
           news_data = MOCK_NEWS[ticker]
           sentiment = news_data["sentiment"]
           sentiment_score = {
               "Positive": 0.7,
               "Neutral": 0.0,
               "Negative": -0.7
           }.get(sentiment, 0.0)
           return sentiment, sentiment_score, news_data["news"], news_data["url"]
       
   except Exception as e:
       # Fallback to mock data on error
       if ticker in MOCK_NEWS:
           news_data = MOCK_NEWS[ticker]
           sentiment = news_data["sentiment"]
           sentiment_score = {
               "Positive": 0.7,
               "Neutral": 0.0,
               "Negative": -0.7
           }.get(sentiment, 0.0)
           return sentiment, sentiment_score, news_data["news"], news_data["url"]
   
   return "Neutral", 0.0, "No news available", ""

def get_analyst_rating(ticker):
   mock = {
       "AAPL": "Strong Buy",
       "MSFT": "Buy",
       "NVDA": "Strong Buy",
       "AMZN": "Buy",
       "NFLX": "Hold",
       "TSLA": "Buy",
       "GOOGL": "Buy",
       "GOOG": "Buy",
       "META": "Buy",
       "AVGO": "Buy",
       "PLTR": "Hold",
       "CDNS": "Buy",
       "ADBE": "Strong Buy",
       "CSCO": "Hold",
       "CMCSA": "Hold",
       "COST": "Strong Buy",
       "CRWD": "Strong Buy",
       "AMD": "Buy",
       "AMAT": "Buy",
       "ASML": "Strong Buy",
       "ATVI": "Hold",
       "BIIB": "Buy",
       "BKNG": "Buy",
       "CHTR": "Hold",
       "CPRT": "Buy",
       "CTSH": "Buy",
       "DXCM": "Buy",
       "DDOG": "Buy",
       "FANG": "Buy",
       "GILD": "Buy",
       "HON": "Buy",
       "ILMN": "Buy",
       "INTC": "Hold",
       "INTU": "Buy",
       "JD": "Hold",
       "KLAC": "Buy",
       "LLY": "Strong Buy",
       "LRCX": "Buy",
       "LULU": "Buy",
       "MAR": "Buy",
       "MRNA": "Hold",
       "MRVL": "Buy",
       "MU": "Buy",
       "NAVI": "Buy",
       "ODFL": "Buy",
       "ORLY": "Buy",
       "PCAR": "Buy",
       "PSTG": "Buy",
       "PAYX": "Buy",
       "REGN": "Buy",
       "ROST": "Buy",
       "SIRI": "Hold",
       "SNPS": "Buy",
       "TEAM": "Buy",
       "TCOM": "Hold",
       "TSMC": "Strong Buy",
       "TTD": "Buy",
       "VRSN": "Buy",
       "VRSK": "Buy",
       "VRTX": "Strong Buy",
       "WDAY": "Buy",
       "XEL": "Buy",
       "ZM": "Hold",
       "ZS": "Buy",
       "DECK": "Buy"
   }
   return mock.get(ticker, "Hold")

# -------------------------------
# SCORING ENGINE
# -------------------------------

def compute_score(yoy, qoq, sentiment_score, rating):

   score = 0

   # Growth contribution
   if yoy:
       score += yoy * 0.4
   if qoq:
       score += qoq * 0.2

   # Sentiment contribution (scaled)
   score += sentiment_score * 20

   # Analyst rating contribution
   rating_map = {
       "Strong Buy": 20,
       "Buy": 10,
       "Hold": 0,
       "Sell": -10,
       "Strong Sell": -20
   }

   score += rating_map.get(rating, 0)

   return round(score, 2)


def get_signal(score):
   if score > 30:
       return "Strong Bullish 🟢"
   elif score > 10:
       return "Bullish 🟢"
   elif score < -10:
       return "Bearish 🔴"
   else:
       return "Neutral 🟡"

# -------------------------------
# BUILD DATA
# -------------------------------

data = []

for ticker in TICKERS:
   price = get_price(ticker)
   
   # Skip tickers with no price data
   if price is None:
       continue
       
   yoy, qoq = get_financials(ticker)
   sentiment_label, sentiment_score, news_summary, source_url = get_news_sentiment(ticker)
   rating = get_analyst_rating(ticker)

   score = compute_score(yoy, qoq, sentiment_score, rating)
   signal = get_signal(score)

   data.append({
       "Ticker": ticker,
       "Company": COMPANY_NAMES.get(ticker, ticker),
       "Price": price,
       "Sentiment": sentiment_label,
       "Latest News": news_summary,
       "Source": source_url,
       "YoY (%)": yoy,
       "QoQ (%)": qoq,
       "Rating": rating,
       "Score": score,
       "Signal": signal
   })

df = pd.DataFrame(data)

# Rank by score
df = df.sort_values(by="Score", ascending=False)

# -------------------------------
# UI
# -------------------------------

st.title("📊 Nasdaq-100 Smart Dashboard (Scored)")

# Top metrics
col1, col2, col3 = st.columns(3)

col1.metric("Top Stock", df.iloc[0]["Ticker"])
col2.metric("Highest Score", df["Score"].max())
col3.metric("Lowest Score", df["Score"].min())

# -------------------------------
# COLOR STYLING
# -------------------------------

def color_signal(val):
   if "Bullish" in val:
       return "color: green; font-weight: bold"
   elif "Bearish" in val:
       return "color: red; font-weight: bold"
   else:
       return "color: orange"

styled_df = df.style.applymap(color_signal, subset=["Signal"])
st.subheader("� All Companies Ranked")

# Format the dataframe for display
display_df = df.copy()

# Define column configuration with LinkColumn for Source and TextColumn for Latest News
column_config_dict = {
    "Latest News": column_config.TextColumn(
        label="Latest News",
        width="large"
    ),
    "Source": column_config.LinkColumn(
        label="Source",
        display_text="📰 News Link"
    )
}

# Add CSS to allow text wrapping in dataframe
st.markdown("""
    <style>
        [data-testid="stDataFrame"] [role="grid"] [role="gridcell"] {
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            max-width: 400px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Display with column narrowing for better view
st.dataframe(
    display_df[["Ticker", "Company", "Price", "YoY (%)", "QoQ (%)", "Sentiment", "Latest News", "Source", "Rating", "Score", "Signal"]],
    column_config=column_config_dict,
    use_container_width=True,
    height=2500
)