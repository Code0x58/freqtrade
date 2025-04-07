from __future__ import annotations

import dataclasses
import typing

from freqtrade.configuration.typed_builder import ConfigShim


@dataclasses.dataclass(frozen=True, slots=True)
class Unfilledtimeout(ConfigShim):
    _config: dict[str, typing.Any]
    """Timeout configuration for unfilled orders. 
    Usually specified in the strategy and missing in the configuration."""
    entry: float | None
    """Timeout for entry orders in unit."""
    exit: float | None
    """Timeout for exit orders in unit."""
    exit_timeout_count: float
    """Number of times to retry exit orders before giving up."""
    unit: typing.Literal["minutes", "seconds"]
    """Unit of time for the timeout (e.g., seconds, minutes)."""


@dataclasses.dataclass(frozen=True, slots=True)
class CheckDepthOfMarket(ConfigShim):
    _config: dict[str, typing.Any]
    """Configuration for checking the depth of the market."""
    enabled: bool | None
    """Enable or disable depth of market check."""
    bids_to_ask_delta: float | None
    """Delta between bids and asks to consider."""


@dataclasses.dataclass(frozen=True, slots=True)
class EntryPricing(ConfigShim):
    _config: dict[str, typing.Any]
    """Configuration for entry pricing."""
    price_last_balance: float | None
    """Balance ratio for the last price."""
    price_side: typing.Literal["ask", "bid", "same", "other"]
    """Side of the price to use (e.g., bid, ask, same)."""
    use_order_book: bool | None
    """Whether to use the order book for pricing."""
    order_book_top: int | None
    """Top N levels of the order book to consider."""
    check_depth_of_market: CheckDepthOfMarket | None
    """Configuration for checking the depth of the market."""


@dataclasses.dataclass(frozen=True, slots=True)
class ExitPricing(ConfigShim):
    _config: dict[str, typing.Any]
    """Configuration for exit pricing."""
    price_side: typing.Literal["ask", "bid", "same", "other"]
    """Side of the price to use (e.g., bid, ask, same)."""
    price_last_balance: float | None
    """Balance ratio for the last price."""
    use_order_book: bool | None
    """Whether to use the order book for pricing."""
    order_book_top: int | None
    """Top N levels of the order book to consider."""


@dataclasses.dataclass(frozen=True, slots=True)
class OrderTypes(ConfigShim):
    _config: dict[str, typing.Any]
    """Configuration of order types. 
    Usually specified in the strategy and missing in the configuration."""
    entry: typing.Literal["limit", "market"]
    """Order type for entry (e.g., limit, market)."""
    exit: typing.Literal["limit", "market"]
    """Order type for exit (e.g., limit, market)."""
    force_exit: typing.Literal["limit", "market"] | None
    """Order type for forced exit (e.g., limit, market)."""
    force_entry: typing.Literal["limit", "market"] | None
    """Order type for forced entry (e.g., limit, market)."""
    emergency_exit: typing.Literal["limit", "market"]
    """Order type for emergency exit (e.g., limit, market)."""
    stoploss: typing.Literal["limit", "market"]
    """Order type for stop loss (e.g., limit, market)."""
    stoploss_on_exchange: bool
    """Whether to place stop loss on the exchange."""
    stoploss_price_type: typing.Literal["last", "mark", "index"] | None
    """Price type for stop loss (e.g., last, mark, index)."""
    stoploss_on_exchange_interval: float | None
    """Interval for stop loss on exchange in seconds."""
    stoploss_on_exchange_limit_ratio: float | None
    """Limit ratio for stop loss on exchange."""


@dataclasses.dataclass(frozen=True, slots=True)
class OrderTimeInForce(ConfigShim):
    _config: dict[str, typing.Any]
    """Time in force configuration for orders. 
    Usually specified in the strategy and missing in the configuration."""
    entry: typing.Literal["GTC", "FOK", "IOC", "PO", "gtc", "fok", "ioc", "po"]
    """Time in force for entry orders."""
    exit: typing.Literal["GTC", "FOK", "IOC", "PO", "gtc", "fok", "ioc", "po"]
    """Time in force for exit orders."""


@dataclasses.dataclass(frozen=True, slots=True)
class Coingecko(ConfigShim):
    _config: dict[str, typing.Any]
    """Configuration for CoinGecko API."""
    is_demo: bool
    """Whether to use CoinGecko in demo mode."""
    api_key: str
    """API key for accessing CoinGecko."""


@dataclasses.dataclass(frozen=True, slots=True)
class Exchange(ConfigShim):
    _config: dict[str, typing.Any]
    """Exchange configuration settings."""
    name: str
    """Name of the exchange."""
    enable_ws: bool
    """Enable WebSocket connections to the exchange."""
    key: str
    """API key for the exchange."""
    secret: str
    """API secret for the exchange."""
    password: str
    """Password for the exchange, if required."""
    uid: str | None
    """User ID for the exchange, if required."""
    pair_whitelist: list[str] | None
    """List of whitelisted trading pairs."""
    pair_blacklist: list[str] | None
    """List of blacklisted trading pairs."""
    log_responses: bool
    """Log responses from the exchange.Useful/required to debug issues with order processing."""
    unknown_fee_rate: float | None
    """Fee rate for unknown markets."""
    outdated_offset: int | None
    """Offset for outdated data in minutes."""
    markets_refresh_interval: int
    """Interval for refreshing market data in minutes."""
    ccxt_config: dict | None
    """CCXT configuration settings."""
    ccxt_async_config: dict | None
    """CCXT asynchronous configuration settings."""


@dataclasses.dataclass(frozen=True, slots=True)
class Edge(ConfigShim):
    _config: dict[str, typing.Any]
    enabled: bool | None
    process_throttle_secs: int
    calculate_since_number_of_days: int | None
    allowed_risk: float
    stoploss_range_min: float | None
    stoploss_range_max: float | None
    stoploss_range_step: float | None
    minimum_winrate: float | None
    minimum_expectancy: float | None
    min_trade_number: float | None
    max_trade_duration_minute: int | None
    remove_pumps: bool | None


@dataclasses.dataclass(frozen=True, slots=True)
class Logging(ConfigShim):
    _config: dict[str, typing.Any]
    version: float
    formatters: dict
    handlers: dict
    root: dict


@dataclasses.dataclass(frozen=True, slots=True)
class SvmParams(ConfigShim):
    _config: dict[str, typing.Any]
    """All parameters available in Sklearn's `SGDOneClassSVM()`."""
    shuffle: bool
    """Whether to shuffle data before applying SVM."""
    nu: float


@dataclasses.dataclass(frozen=True, slots=True)
class FeatureParameters(ConfigShim):
    _config: dict[str, typing.Any]
    """The parameters used to engineer the feature set"""
    include_corr_pairlist: list
    """List of correlated pairs to include in the features."""
    include_timeframes: list
    """A list of timeframes that all indicators in `feature_engineering_expand_*()` will be created for."""
    label_period_candles: int | None
    """Number of candles into the future to use for labeling the period.This can be used in `set_freqai_targets()`."""
    include_shifted_candles: int
    """Add features from previous candles to subsequent candles with the intent of adding historical information."""
    DI_threshold: float
    """Activates the use of the Dissimilarity Index for outlier detection when set to > 0."""
    weight_factor: float
    """Weight training data points according to their recency."""
    principal_component_analysis: bool
    """Automatically reduce the dimensionality of the data set using Principal Component Analysis"""
    use_SVM_to_remove_outliers: bool
    """Use SVM to remove outliers from the features."""
    plot_feature_importances: int
    """Create feature importance plots for each model."""
    svm_params: SvmParams | None
    """All parameters available in Sklearn's `SGDOneClassSVM()`."""
    shuffle_after_split: bool
    """Split the data into train and test sets, and then shuffle both sets individually."""
    buffer_train_data_candles: int
    """Cut `buffer_train_data_candles` off the beginning and end of the training data *after* the indicators were populated."""


@dataclasses.dataclass(frozen=True, slots=True)
class DataSplitParameters(ConfigShim):
    _config: dict[str, typing.Any]
    test_size: float | None
    random_state: int | None
    shuffle: bool


@dataclasses.dataclass(frozen=True, slots=True)
class ModelRewardParameters(ConfigShim):
    _config: dict[str, typing.Any]
    """Parameters for configuring the reward model."""
    rr: float
    """Reward ratio parameter."""
    profit_aim: float
    """Profit aim parameter."""


@dataclasses.dataclass(frozen=True, slots=True)
class RlConfig(ConfigShim):
    _config: dict[str, typing.Any]
    drop_ohlc_from_features: bool
    """Do not include the normalized ohlc data in the feature set."""
    train_cycles: int | None
    """Number of training cycles to perform."""
    max_trade_duration_candles: int | None
    """Guides the agent training to keep trades below desired length."""
    add_state_info: bool
    """Include state information in the feature set for training and inference."""
    max_training_drawdown_pct: float
    """Maximum allowed drawdown percentage during training."""
    cpu_count: int
    """Number of threads/CPU's to use for training."""
    model_type: str
    """Model string from stable_baselines3 or SBcontrib."""
    policy_type: str
    """One of the available policy types from stable_baselines3."""
    net_arch: list
    """Architecture of the neural network."""
    randomize_starting_position: bool
    """Randomize the starting point of each episode to avoid overfitting."""
    progress_bar: bool
    """Display a progress bar with the current progress."""
    model_reward_parameters: ModelRewardParameters | None
    """Parameters for configuring the reward model."""


@dataclasses.dataclass(frozen=True, slots=True)
class Freqai(ConfigShim):
    _config: dict[str, typing.Any]
    enabled: bool
    """Whether freqAI is enabled."""
    identifier: str
    """A unique ID for the current model. Must be changed when modifying features."""
    write_metrics_to_disk: bool
    """Write metrics to disk?"""
    purge_old_models: bool | float
    """Number of models to keep on disk."""
    conv_width: int
    """The width of a neural network input tensor."""
    train_period_days: int
    """Number of days to use for the training data (width of the sliding window)"""
    backtest_period_days: float
    """Number of days to inference from the trained model before sliding the `train_period_days` window """
    live_retrain_hours: float
    """Frequency of retraining during dry/live runs."""
    expiration_hours: float
    """Avoid making predictions if a model is more than `expiration_hours` old. Defaults to 0 (no expiration)."""
    save_backtest_models: bool
    """Save models to disk when running backtesting."""
    fit_live_predictions_candles: int | None
    """Number of historical candles to use for computing target (label) statistics from prediction data, instead of from the training dataset."""
    data_kitchen_thread_count: int | None
    """Designate the number of threads you want to use for data processing (outlier methods, normalization, etc.)."""
    activate_tensorboard: bool
    """Indicate whether or not to activate tensorboard"""
    wait_for_training_iteration_on_reload: bool
    """Wait for the next training iteration to complete after /reload or ctrl+c."""
    continual_learning: bool
    """Use the final state of the most recently trained model as starting point for the new model, allowing for incremental learning."""
    keras: bool
    """Use Keras for model training."""
    feature_parameters: FeatureParameters
    """The parameters used to engineer the feature set"""
    data_split_parameters: DataSplitParameters
    model_training_parameters: dict | None
    """Flexible dictionary that includes all parameters available by the selected model library. """
    rl_config: RlConfig | None


@dataclasses.dataclass(frozen=True, slots=True)
class ProducersElement(ConfigShim):
    _config: dict[str, typing.Any]
    name: str
    """Name of the producer."""
    host: str
    """Host of the producer."""
    port: int
    """Port of the producer."""
    secure: bool
    """Whether to use SSL to connect to the producer."""
    ws_token: str
    """WebSocket token for the producer."""


@dataclasses.dataclass(frozen=True, slots=True)
class ExternalMessageConsumer(ConfigShim):
    _config: dict[str, typing.Any]
    """Configuration for external message consumer."""
    enabled: bool
    """Whether the external message consumer is enabled."""
    producers: list[ProducersElement]
    """List of producers for the external message consumer."""
    wait_timeout: int | None
    """Wait timeout in seconds."""
    sleep_time: int | None
    """Sleep time in seconds before retrying to connect."""
    ping_timeout: int | None
    """Ping timeout in seconds."""
    remove_entry_exit_signals: bool
    """Remove signal columns from the dataframe (set them to 0)"""
    initial_candle_limit: int
    """Initial candle limit."""
    message_size_limit: int
    """Message size limit in megabytes."""


@dataclasses.dataclass(frozen=True, slots=True)
class Experimental(ConfigShim):
    _config: dict[str, typing.Any]
    """Experimental configuration."""
    block_bad_exchanges: bool | None


@dataclasses.dataclass(frozen=True, slots=True)
class PairlistsElement(ConfigShim):
    _config: dict[str, typing.Any]
    method: typing.Literal[
        "StaticPairList",
        "VolumePairList",
        "PercentChangePairList",
        "ProducerPairList",
        "RemotePairList",
        "MarketCapPairList",
        "AgeFilter",
        "FullTradesFilter",
        "OffsetFilter",
        "PerformanceFilter",
        "PrecisionFilter",
        "PriceFilter",
        "RangeStabilityFilter",
        "ShuffleFilter",
        "SpreadFilter",
        "VolatilityFilter",
    ]
    """Method used for generating the pairlist."""


@dataclasses.dataclass(frozen=True, slots=True)
class NotificationSettings(ConfigShim):
    _config: dict[str, typing.Any]
    """Settings for different types of notifications."""
    status: typing.Literal["on", "off", "silent"] | None
    """Telegram setting for status updates."""
    warning: typing.Literal["on", "off", "silent"] | None
    """Telegram setting for warnings."""
    startup: typing.Literal["on", "off", "silent"] | None
    """Telegram setting for startup messages."""
    entry: typing.Literal["on", "off", "silent"] | None
    """Telegram setting for entry signals."""
    entry_fill: typing.Literal["on", "off", "silent"]
    """Telegram setting for entry fill signals."""
    entry_cancel: typing.Literal["on", "off", "silent"] | None
    """Telegram setting for entry cancel signals."""
    exit: str | dict[str, typing.Literal["on", "off", "silent"]] | None
    """Telegram setting for exit signals."""
    exit_fill: str | dict[str, typing.Literal["on", "off", "silent"]]
    """Telegram setting for exit fill signals."""
    exit_cancel: typing.Literal["on", "off", "silent"] | None
    """Telegram setting for exit cancel signals."""
    protection_trigger: typing.Literal["on", "off", "silent"]
    """Telegram setting for protection triggers."""
    protection_trigger_global: typing.Literal["on", "off", "silent"]
    """Telegram setting for global protection triggers."""


@dataclasses.dataclass(frozen=True, slots=True)
class Telegram(ConfigShim):
    _config: dict[str, typing.Any]
    """Telegram settings."""
    enabled: bool
    """Enable Telegram notifications."""
    token: str
    """Telegram bot token."""
    chat_id: str
    """Telegram chat or group ID"""
    topic_id: str | None
    """Telegram topic ID - only applicable for group chats"""
    authorized_users: list[str] | None
    """Authorized users for the bot."""
    allow_custom_messages: bool
    """Allow sending custom messages from the Strategy."""
    balance_dust_level: float | None
    """Minimum balance level to consider as dust."""
    notification_settings: NotificationSettings
    """Settings for different types of notifications."""
    reload: bool | None
    """Add Reload button to certain messages."""


@dataclasses.dataclass(frozen=True, slots=True)
class Webhook(ConfigShim):
    _config: dict[str, typing.Any]
    """Webhook settings."""
    enabled: bool | None
    url: str | None
    format: typing.Literal["form", "json", "raw"]
    retries: int | None
    retry_delay: float | None
    status: dict | None
    warning: dict | None
    exception: dict | None
    startup: dict | None
    entry: dict | None
    entry_fill: dict | None
    entry_cancel: dict | None
    exit: dict | None
    exit_fill: dict | None
    exit_cancel: dict | None
    protection_trigger: dict | None
    protection_trigger_global: dict | None
    strategy_msg: dict | None
    whitelist: dict | None
    analyzed_df: dict | None
    new_candle: dict | None


@dataclasses.dataclass(frozen=True, slots=True)
class Discord(ConfigShim):
    _config: dict[str, typing.Any]
    """Discord settings."""
    enabled: bool | None
    webhook_url: str | None
    exit_fill: list[dict]
    entry_fill: list[dict]


@dataclasses.dataclass(frozen=True, slots=True)
class ApiServer(ConfigShim):
    _config: dict[str, typing.Any]
    """API server settings."""
    enabled: bool
    """Whether the API server is enabled."""
    listen_ip_address: str
    """IP address the API server listens on."""
    listen_port: int
    """Port the API server listens on."""
    username: str
    """Username for API server authentication."""
    password: str
    """Password for API server authentication."""
    ws_token: str | list[str] | None
    """WebSocket token for API server."""
    jwt_secret_key: str | None
    """Secret key for JWT authentication."""
    CORS_origins: list[str] | None
    """List of allowed CORS origins."""
    verbosity: typing.Literal["error", "info"] | None
    """Logging verbosity level."""


@dataclasses.dataclass(frozen=True, slots=True)
class Internals(ConfigShim):
    _config: dict[str, typing.Any]
    """Internal settings."""
    process_throttle_secs: int | None
    """Minimum loop duration for one bot iteration in seconds."""
    interval: int | None
    """Interval time in seconds."""
    sd_notify: bool | None
    """Enable systemd notify."""


@dataclasses.dataclass(frozen=True, slots=True)
class Orderflow(ConfigShim):
    _config: dict[str, typing.Any]
    """Settings related to order flow."""
    cache_size: float
    """Size of the cache for order flow data."""
    max_candles: float
    """Maximum number of candles to consider."""
    scale: float
    """Scale factor for order flow data."""
    stacked_imbalance_range: float
    """Range for stacked imbalance."""
    imbalance_volume: float
    """Volume threshold for imbalance."""
    imbalance_ratio: float
    """Ratio threshold for imbalance."""


@dataclasses.dataclass(frozen=True, slots=True)
class RootConfig(ConfigShim):
    _config: dict[str, typing.Any]
    max_open_trades: int | float | None
    """Maximum number of open trades. -1 for unlimited."""
    timeframe: str | None
    """The timeframe to use (e.g `1m`, `5m`, `15m`, `30m`, `1h` ...). 
    Usually specified in the strategy and missing in the configuration."""
    proxy_coin: str | None
    """Proxy coin - must be used for specific futures modes (e.g. BNFCR)"""
    stake_currency: str | None
    """Currency used for staking."""
    stake_amount: float | str | None
    """Amount to stake per trade."""
    tradable_balance_ratio: float
    """Ratio of balance that is tradable."""
    available_capital: float | None
    """Total capital available for trading."""
    amend_last_stake_amount: bool
    """Whether to amend the last stake amount."""
    last_stake_amount_min_ratio: float
    """Minimum ratio for the last stake amount."""
    fiat_display_currency: (
        typing.Literal[
            "AUD",
            "BRL",
            "CAD",
            "CHF",
            "CLP",
            "CNY",
            "CZK",
            "DKK",
            "EUR",
            "GBP",
            "HKD",
            "HUF",
            "IDR",
            "ILS",
            "INR",
            "JPY",
            "KRW",
            "MXN",
            "MYR",
            "NOK",
            "NZD",
            "PHP",
            "PKR",
            "PLN",
            "RUB",
            "UAH",
            "SEK",
            "SGD",
            "THB",
            "TRY",
            "TWD",
            "ZAR",
            "USD",
            "BTC",
            "ETH",
            "XRP",
            "LTC",
            "BCH",
            "BNB",
            "",
        ]
        | None
    )
    """Fiat currency for display purposes."""
    dry_run: bool | None
    """Enable or disable dry run mode."""
    dry_run_wallet: float | dict
    """Initial wallet balance for dry run mode."""
    cancel_open_orders_on_exit: bool
    """Cancel open orders when exiting."""
    process_only_new_candles: bool | None
    """Process only new candles."""
    minimal_roi: dict | None
    """Minimum return on investment. 
    Usually specified in the strategy and missing in the configuration."""
    amount_reserve_percent: float | None
    """Percentage of amount to reserve."""
    stoploss: float | None
    """Value (as ratio) to use as Stoploss value. 
    Usually specified in the strategy and missing in the configuration."""
    trailing_stop: bool | None
    """Enable or disable trailing stop. 
    Usually specified in the strategy and missing in the configuration."""
    trailing_stop_positive: float | None
    """Positive offset for trailing stop. 
    Usually specified in the strategy and missing in the configuration."""
    trailing_stop_positive_offset: float | None
    """Offset for trailing stop to activate. 
    Usually specified in the strategy and missing in the configuration."""
    trailing_only_offset_is_reached: bool | None
    """Use trailing stop only when offset is reached. 
    Usually specified in the strategy and missing in the configuration."""
    use_exit_signal: bool | None
    """Use exit signal for trades. 
    Usually specified in the strategy and missing in the configuration."""
    exit_profit_only: bool | None
    """Exit only when in profit. Exit signals are ignored as long as profit is < exit_profit_offset. 
    Usually specified in the strategy and missing in the configuration."""
    exit_profit_offset: float | None
    """Offset for profit exit. 
    Usually specified in the strategy and missing in the configuration."""
    fee: float | None
    """Trading fee percentage. Can help to simulate slippage in backtesting"""
    ignore_roi_if_entry_signal: bool | None
    """Ignore ROI if entry signal is present. 
    Usually specified in the strategy and missing in the configuration."""
    ignore_buying_expired_candle_after: float | None
    """Ignore buying after candle expiration time. 
    Usually specified in the strategy and missing in the configuration."""
    trading_mode: typing.Literal["spot", "margin", "futures"] | None
    """Mode of trading (e.g., spot, margin)."""
    margin_mode: typing.Literal["cross", "isolated", ""] | None
    """Margin mode for trading."""
    reduce_df_footprint: bool
    """Reduce DataFrame footprint by casting columns to float32/int32."""
    minimum_trade_amount: float
    """Minimum amount for a trade - only used for lookahead-analysis"""
    targeted_trade_amount: float
    """Targeted trade amount for lookahead analysis."""
    lookahead_analysis_exportfilename: str | None
    """csv Filename for lookahead analysis export."""
    startup_candle: list
    """Startup candle configuration."""
    liquidation_buffer: float | None
    """Buffer ratio for liquidation."""
    backtest_breakdown: list[typing.Literal["day", "week", "month", "year"]] | None
    """Breakdown configuration for backtesting."""
    bot_name: str | None
    """Name of the trading bot. Passed via API to a client."""
    unfilledtimeout: Unfilledtimeout | None
    """Timeout configuration for unfilled orders. 
    Usually specified in the strategy and missing in the configuration."""
    entry_pricing: EntryPricing | None
    """Configuration for entry pricing."""
    exit_pricing: ExitPricing | None
    """Configuration for exit pricing."""
    custom_price_max_distance_ratio: float
    """Maximum distance ratio between current and custom entry or exit price."""
    order_types: OrderTypes | None
    """Configuration of order types. 
    Usually specified in the strategy and missing in the configuration."""
    order_time_in_force: OrderTimeInForce | None
    """Time in force configuration for orders. 
    Usually specified in the strategy and missing in the configuration."""
    coingecko: Coingecko | None
    """Configuration for CoinGecko API."""
    exchange: Exchange | None
    """Exchange configuration settings."""
    edge: Edge | None
    log_config: Logging | None
    freqai: Freqai | None
    external_message_consumer: ExternalMessageConsumer | None
    """Configuration for external message consumer."""
    experimental: Experimental | None
    """Experimental configuration."""
    pairlists: list[PairlistsElement] | None
    """Configuration for pairlists."""
    telegram: Telegram | None
    """Telegram settings."""
    webhook: Webhook | None
    """Webhook settings."""
    discord: Discord | None
    """Discord settings."""
    api_server: ApiServer | None
    """API server settings."""
    db_url: str | None
    """Database connection URL."""
    export: typing.Literal["none", "trades", "signals"]
    """Type of data to export."""
    disableparamexport: bool | None
    """Disable parameter export."""
    initial_state: typing.Literal["running", "paused", "stopped"] | None
    """Initial state of the system."""
    force_entry_enable: bool | None
    """Force enable entry."""
    disable_dataframe_checks: bool | None
    """Disable checks on dataframes."""
    internals: Internals
    """Internal settings."""
    dataformat_ohlcv: typing.Literal["json", "jsongz", "feather", "parquet"]
    """Data format for OHLCV data."""
    dataformat_trades: typing.Literal["json", "jsongz", "feather", "parquet"]
    """Data format for trade data."""
    position_adjustment_enable: bool | None
    """Enable position adjustment. 
    Usually specified in the strategy and missing in the configuration."""
    new_pairs_days: int
    """Download data of new pairs for given number of days"""
    download_trades: bool | None
    """Download trades data by default (instead of ohlcv data)."""
    max_entry_position_adjustment: int | float | None
    """Maximum entry position adjustment allowed. 
    Usually specified in the strategy and missing in the configuration."""
    add_config_files: list[str] | None
    """Additional configuration files to load."""
    orderflow: Orderflow | None
    """Settings related to order flow."""
