# Data notes

Methodological choices behind the data used in this project, and the reasons for them.

## Time coverage: from January 2022

Trade data is retrieved from January 2022 (`MonthId` 202201) onwards, for three reasons.

### 1. Consistent measurement of imports

Supply dependence is measured with import data, and January 2022 is the first month in which all UK imports are
collected the same way. Until the end of 2021, imports into Great Britain from the EU were collected through the
Intrastat survey of traders, while imports from the rest of the world came from customs declarations. From
January 2022, GB imports from the EU are also compiled from customs declarations (Intrastat continues only for trade
between Northern Ireland and the EU). HMRC reports a break in the EU import series at that point, so shares by
supplier country before and after January 2022 would rest on different collection methods.

Exports have a similar break one year earlier: GB exports to the EU have been compiled from customs declarations
since January 2021.

Sources:
- HMRC, [UK overseas trade in goods statistics: methodology notes](https://www.gov.uk/government/statistics/uk-overseas-trade-in-goods-statistics-july-2025/uk-overseas-trade-in-goods-statistics-july-2025-methodology-notes)
- ONS, [Understanding the latest changes to UK trade figures with the EU](https://blog.ons.gov.uk/2022/03/11/understanding-the-latest-changes-to-uk-trade-figures-with-the-eu) (March 2022)

### 2. Consistent commodity codes

The HS codes in `config/minerals.toml` come from Annex 5 of the Critical Minerals technical annex and are current
codes. The HS2022 revision of the Harmonized System took effect in January 2022, and before it some of these codes did
not exist in their current form. Starting in January 2022 avoids gaps in a series that come from code changes rather
than from changes in trade.

### 3. Alignment with the policy timeline

The UK published its first Critical Minerals Strategy in July 2022. Starting in January 2022 covers the whole period
from the first strategy to the current one (Vision 2035, November 2025), which matches the question of how UK supply
dependence compares with the strategy's targets.

### Caveats

- **Shorter history.** The series has no baseline before 2022, so longer-term trends cannot be shown.
- **Possible over-recording of imports in 2022.** Under Staged Customs Controls, some customs declarations were
  submitted late, and the ONS notes that 2022 imports may be over-recorded as a result. The affected declarations
  cannot be identified, so no adjustment is possible.
  Source: ONS, [Impact of trade in goods data collection changes on UK trade statistics](https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/articles/impactoftradeingoodsdatacollectionchangesonuktradestatistics/latest)
- **Price effects in 2022.** Russia's invasion of Ukraine in February 2022 pushed up prices for several commodities,
  which affects shares measured by value.

## Suppressed data

HMRC withholds some trade data at the request of businesses or government departments. A suppression applies to one
commodity code and flow, at one of three levels: Level 1 publishes nothing; Level 2 publishes only totals, with partner
countries and ports withheld; Level 3 publishes only total value. Level 2 rows appear in the data under the partner
"Confidential Country" (`CountryId` 977), with `SuppressionIndex` 2. Level 1 leaves no rows at all.

Suppressions affecting the codes in `config/minerals.toml` (current list checked 16 October 2026):

- **Zinc**: zinc oxide imports (28170000) are Level 2 throughout, so the partner country is unknown for about 36% of
  zinc's import value.
- **Silicon**: two ferro-silicon codes (72022100, 72022990) were Level 2 until August 2024; partner countries are
  published from September 2024. This is a break in the series.
- **Chromium**: oxide and hydroxide imports (28191000, 28199010, 28199090) and unwrought chromium exports (81122110,
  81122190) became Level 1 from February 2025, so they disappear from the data from then on. This is a break in
  the series, not a fall in trade.
- **Exports only**: one uranium code is Level 2 throughout (28444310); sodium hydroxide (28151100), one uranium code
  (28443019) and two copper tube codes (74111010, 74111090) are Level 1 throughout.

Sources: HMRC, [Suppressions policy](https://www.uktradeinfo.com/trade-data/suppressions-policy/) and
[Current suppressions](https://www.uktradeinfo.com/trade-data/current-suppressions/).

## Other notes on the trade data

- **Missing mass.** Some rows have a value but no net mass. By value this is under 1% for most minerals; the
  exceptions are uranium (about 32%), helium (5%), rhenium (4%) and beryllium (2%). For platinum group metals,
  quantities are recorded in supplementary units (`SuppUnit`) instead.
- **Shared codes.** Four codes are listed under two minerals each (iron and manganese, cobalt and titanium, iridium
  and ruthenium), so totals across minerals must not count them twice.
- **EU and non-EU.** The EU split comes from the flow type, not from the Country lookup's area fields, which use
  historic groupings (they list the UK under the EU).
- **Special partners.** "Stores & Provisions" (supplies for ships and aircraft) and the UK as a partner country
  account for negligible trade.
- **Recent months are provisional.** HMRC revises recent figures, so the latest months may change in later pulls.
