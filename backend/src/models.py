from flask_restx import fields
from flask_restx.inputs import date_from_iso8601

# ---------------------------------------------------------------------------- #
#                                    MODELS                                    #
# ---------------------------------------------------------------------------- #

# Models for payload validation detailing their structures for the Backend Swagger


def login_model(namespace):
    return namespace.model(
        "login",
        {
            "email": fields.String(required=True, example="duck@pond.com"),
            "password": fields.String(required=True, example="hunter12"),
        },
    )


def register_model(namespace):
    return namespace.model(
        "register",
        {
            "first_name": fields.String(required=True, example="Sir"),
            "last_name": fields.String(required=True, example="Gooseington"),
            "email": fields.String(required=True, example="goose@pond.com"),
            "username": fields.String(required=True, example="goose"),
            "password": fields.String(required=True, example="hunter12"),
        },
    )


def comment_model(namespace):
    return namespace.model(
        "comment",
        {
            "stockTicker": fields.String(required=True, example="TSLA"),
            "timestamp": fields.Integer(required=True, example=1618142069157),
            "content": fields.String(required=True, example="This is a comment"),
        },
    )


def comment_delete_model(namespace):
    return namespace.model(
        "comment_delete",
        {
            "comment_id": fields.String(
                required=True, example="9a685142-9929-11eb-957d-0a4e2d6dea13"
            ),
        },
    )


def comment_edit_model(namespace):
    return namespace.model(
        "comment_edit",
        {
            "comment_id": fields.String(
                required=True, example="9a685142-9929-11eb-957d-0a4e2d6dea13"
            ),
            "time_stamp": fields.Integer(required=True, example=1618142069157),
            "content": fields.String(required=True, example="This is a comment"),
        },
    )


def comment_vote_model(namespace):
    return namespace.model(
        "comment_vote",
        {
            "comment_id": fields.String(
                required=True, example="a1ba864a-9929-11eb-be3a-0a4e2d6dea13"
            ),
        },
    )


def reply_model(namespace):
    return namespace.model(
        "reply",
        {
            "stockTicker": fields.String(required=True, example="TSLA"),
            "timestamp": fields.Integer(required=True, example=1618142069157),
            "content": fields.String(required=True, example="This is a reply"),
            "parentID": fields.String(
                required=True, example="9a685142-9929-11eb-957d-0a4e2d6dea13"
            ),
        },
    )


def reply_delete_model(namespace):
    return namespace.model(
        "reply_delete",
        {
            "comment_id": fields.String(
                required=True, example="ad939422-9abc-11eb-938b-0a4e2d6dea13"
            ),
            "parent_id": fields.String(
                required=True, example="9a685142-9929-11eb-957d-0a4e2d6dea13"
            ),
        },
    )


def reply_edit_model(namespace):
    return namespace.model(
        "reply_edit",
        {
            "comment_id": fields.String(
                required=True, example="ad939422-9abc-11eb-938b-0a4e2d6dea13"
            ),
            "time_stamp": fields.Integer(required=True, example=1618142069157),
            "content": fields.String(required=True, example="This is a reply"),
            "parent_id": fields.String(
                required=True, example="9a685142-9929-11eb-957d-0a4e2d6dea13"
            ),
        },
    )


def reply_vote_model(namespace):
    return namespace.model(
        "reply_vote",
        {
            "comment_id": fields.String(
                required=True, example="a1ba864a-9929-11eb-be3a-0a4e2d6dea13"
            ),
            "reply_id": fields.String(
                required=True, example="ad939422-9abc-11eb-938b-0a4e2d6dea13"
            ),
        },
    )


def notes_model(namespace):
    return namespace.model(
        "notes",
        {
            "title": fields.String(required=True, example="Note Title"),
            "content": fields.String(required=True, example="Note Content"),
            "stock_symbols": fields.List(fields.String(example="TSLA")),
            "portfolio_names": fields.List(fields.String(example="Portfolio A")),
            "external_references": fields.List(fields.String(example="")),
            "internal_references": fields.List(fields.String(example="")),
        },
    )


def notes_edit_model(namespace):
    return namespace.model(
        "notes_edit",
        {
            "new_title": fields.String(required=True, example="Note Title"),
            "content": fields.String(required=True, example="Note Content"),
            "stock_symbols": fields.List(fields.String(example="TSLA")),
            "portfolio_names": fields.List(fields.String(example="Portfolio A")),
            "external_references": fields.List(fields.String(example="")),
            "internal_references": fields.List(fields.String(example="")),
        },
    )


def investment_model(namespace):
    return namespace.model(
        "investment",
        {
            "num_shares": fields.Integer(required=True, example=1),
            "stock_ticker": fields.String(required=True, example="TSLA"),
            "purchase_date": fields.Integer(required=True, example=16000),
        },
    )


def portfolio_model(namespace):
    return namespace.model(
        "portfolio",
        {
            "name": fields.String(required=True, example="PortfolioA"),
        },
    )


def create_dashboard_block_model(namespace):
    return namespace.model(
        "create_block",
        {
            "type": fields.String(required=True, example="portfolio"),
            "meta": fields.Raw,
        },
    )


# ---------------------------------------------------------------------------- #
#                                    PARSERS                                   #
# ---------------------------------------------------------------------------- #

# Query parsers to validate any query parameters passed into the request


def token_parser(namespace):
    return namespace.parser().add_argument(
        "Authorization", help="User Authorization Token", location="headers"
    )


def portfolio_parser(namespace):
    return namespace.parser().add_argument(
        "name", help="Portfolio name", location="args"
    )


def investment_parser(namespace):
    return namespace.parser().add_argument(
        "portfolio", help="Portfolio name", location="args"
    )


def delete_investment_parser(namespace):
    return namespace.parser().add_argument("id", help="Portfolio ID", location="args")


def trending_parser(namespace):
    return namespace.parser().add_argument("n", help="Portfolio ID", location="args")


def forum_parser(namespace):
    return namespace.parser().add_argument(
        "stockTicker", help="Stock Security Symbol", location="args"
    )


def news_parser(namespace):
    return namespace.parser().add_argument(
        "symbol", help="Stock Security Symbol", location="args"
    )


def news_count_parser(namespace):
    return namespace.parser().add_argument(
        "count", help="Number of News Articles", location="args"
    )


def news_stocks_parser(namespace):
    return namespace.parser().add_argument(
        "stocks",
        help="List of Stock Symbols",
        type=list,
        action="append",
        location="args",
    )


def notes_edit_parser(namespace):
    return namespace.parser().add_argument("note", help="Note name", location="args")


def notes_delete_parser(namespace):
    return namespace.parser().add_argument("title", help="Note Title", location="args")


def notes_relevant_parser(namespace):
    return (
        namespace.parser()
        .add_argument(
            "stock",
            help="List of Stock Symbols",
            type=list,
            action="append",
            location="args",
        )
        .add_argument(
            "portfolio",
            help="List of Portfolio Names",
            type=list,
            action="append",
            location="args",
        )
    )


def stock_get_data_parser(namespace):
    return namespace.parser().add_argument(
        "symbol", help="Stock Symbol", location="args"
    )


def stock_get_prediction_parser(namespace):
    return (
        namespace.parser()
        .add_argument("symbol", help="Stock Symbol", location="args")
        .add_argument("prediction_type", help="Prediction Model", location="args")
    )


def stock_get_paper_trade_parser(namespace):
    return (
        namespace.parser()
        .add_argument("symbol", help="Stock Symbol", type=str, location="args")
        .add_argument(
            "initial_cash",
            help="Starting Portfolio Value",
            type=[int, float],
            location="args",
        )
        .add_argument(
            "commission", help="Trading Commission", type=str, location="args"
        )
        .add_argument("strategy", help="Strategy to Use", type=str, location="args")
        .add_argument(
            "fromdate",
            help="Date to Start Test From",
            type=date_from_iso8601,
            location="args",
        )
        .add_argument(
            "todate", help="Date to End Test", type=date_from_iso8601, location="args"
        )
    )


def screeners_post_delete_data_parser(namespace):
    return namespace.parser().add_argument(
        "name", help="Screener Name", location="args"
    )


def screeners_get_apply_screener_parser(namespace):
    return (
        namespace.parser()
        .add_argument(
            "exchange",
            help="Stock Exchanges (list)",
            type=list,
            action="append",
            location="args",
        )
        .add_argument(
            "market_cap",
            help="Market Capitalisation (min and max values)",
            type=list,
            action="append",
            location="args",
        )
        .add_argument(
            "yearly_low",
            help="Yearly Low Share Price",
            type=[int, float],
            location="args",
        )
        .add_argument(
            "yearly_high",
            help="Yearly High Share Price",
            type=[int, float],
            location="args",
        )
        .add_argument(
            "eps",
            help="EPS (min and max values)",
            type=list,
            action="append",
            location="args",
        )
        .add_argument(
            "beta",
            help="Beta Ratio (min and max values)",
            type=list,
            action="append",
            location="args",
        )
        .add_argument(
            "payout_ratio",
            help="Payout Ratio (min and max values)",
            type=list,
            action="append",
            location="args",
        )
        .add_argument(
            "sector",
            help="Sector (list)",
            type=list,
            action="append",
            location="args",
        )
        .add_argument(
            "industry",
            help="Industry (list)",
            type=list,
            action="append",
            location="args",
        )
    )
