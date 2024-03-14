# ionos_cloud_billing_ui
Simple python frontend for the INOS cloud billing API

The script requires the contract owner login information and contract number as well as a period (month) to aggregate all the relevant billing data.
Data is aggregated by meterId, unused assets and products with no price are excluded.
A forecast is available for the current month and done by calculating the passed time in the current month on a per hour basis. The result is extrapolated for the full month.
Note: The data source is https://api.ionos.com/billing/{contract}/products and https://api.ionos.com/billing/{contract}/usage. The received data might be slightly different from the actual invoice data.
If a more granular view is required, the output from https://api.ionos.com/billing/{contract}/usage or https://api.ionos.com/billing/{contract}/utilization can be used.
