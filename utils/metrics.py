import numpy as np

def add_metrics(df):
    """
    Add calculated fields for BI analysis
    """

    # Shipping delay indicator
    df['Shipping_Delay_Flag'] = np.where(
        df['Shipping times'] > df['Lead times'], 1, 0
    )

    # Inventory status
    df['Inventory_Status'] = np.where(
        df['Stock levels'] < df['Order quantities'],
        'Low Stock',
        'Safe'
    )

    # Cost efficiency
    df['Cost_per_Unit'] = df['Costs'] / df['Order quantities']

    return df
