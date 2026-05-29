import pandas as pd
import csv

try:
    print("Reading CSV file...")

    # Read CSV safely
    df = pd.read_csv(
        "vw_leads_full_details.csv",
        dtype=str,
        encoding="utf-8",
        on_bad_lines="skip"   # skips broken rows if any
    )

    print("Rows read:", len(df))

    print("Writing fixed CSV file...")

    # Write properly quoted CSV
    df.to_csv(
        "vw_leads_full_details_fixed.csv",
        index=False,
        quoting=csv.QUOTE_ALL,
        encoding="utf-8"
    )

    print("✅ CSV fixed successfully!")
    print("Output file: vw_leads_full_details_fixed.csv")

except Exception as e:
    print("❌ Error occurred:")
    print(e)