from django.core.management.base import BaseCommand
from data_receiver.models import TourismStat
import pandas as pd
import datetime


class Command(BaseCommand):
    help = "fill tourism info model with data"

    def add_arguments(self, parser):
        parser.add_argument("occupancy_file", type=str)
        parser.add_argument("night_file", type=str)

    def handle(self, *args, **options):
        iso2_country_name_dict = {
            "AL": "Albania",
            "AT": "Austria",
            "BE": "Belgium",
            "BG": "Bulgaria",
            "CH": "Switzerland",
            "CY": "Cyprus",
            "CZ": "Czech Republic",
            "DE": "Germany",
            "DK": "Denmark",
            "EE": "Estonia",
            "EL": "Greece",
            "ES": "Spain",
            "FI": "Finland",
            "FR": "France",
            "HR": "Croatia",
            "HU": "Hungary",
            "IE": "Ireland",
            "IT": "Italy",
            "LI": "Liechtenstein",
            "LT": "Lithuania",
            "LU": "Luxembourg",
            "LV": "Latvia",
            "ME": "Montenegro",
            "MK": "North Macedonia",
            "MT": "Malta",
            "NL": "Netherlands",
            "NO": "Norway",
            "PL": "Poland",
            "PT": "Portugal",
            "RO": "Romania",
            "RS": "Serbia",
            "SE": "Sweden",
            "SI": "Slovenia",
            "SK": "Slovakia",
            "TR": "Turkey",
            "XK": "Kosovo",
        }

        rate_data_df = self.fix_df_index(pd.read_csv(options["occupancy_file"], sep="\t", encoding="utf-8", index_col=0))
        night_data_df = self.fix_df_index(pd.read_csv(options["night_file"], sep="\t", encoding="utf-8", index_col=0))

        joined_df = rate_data_df.join(night_data_df, how="left", rsuffix="_n")

        for country_iso_2, row in joined_df.iterrows():
            if country_iso_2 in iso2_country_name_dict:
                for date in rate_data_df.columns:
                    year, month = map(int, date.split("-"))
                    parsed_date = datetime.date(year, month, 1)
                    rate = self.clean_value(row[date])
                    night = self.clean_value(row.get(f"{date}_n"))
                    TourismStat.objects.update_or_create(country= country_iso_2, date=parsed_date, defaults={
                        "nights_spent": night,
                        "occupancy_rate": rate,
                    })
        self.stdout.write(self.style.SUCCESS("data loaded successfully"))

    @staticmethod
    def clean_value(value):
        if pd.isna(value) or value.strip() == ':':
            return None
        return float(str(value).replace("e","").replace("u",""))

    @staticmethod
    def fix_df_index(df):
        df["geo"] = df.index.str.split(",").str[-1]
        return df.set_index("geo")