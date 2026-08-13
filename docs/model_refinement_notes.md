# Practitioner-Informed Model Refinement Notes

These notes map conceptual questions raised in private practitioner discussion to version 0.2 design changes. They intentionally avoid naming, quoting, or presenting private discussion as public evidence.

| Practitioner question or observation | Version 0.1 gap | Version 0.2 response | Remaining limitation |
|---|---|---|---|
| A supply-side reading may overprice a disruption when demand falls. | Demand reduction was effectively a static absorber. | Demand is now a dynamic state driven by price, policy pressure, adjustment time, and recovery. | Aggregate reduced-form demand is not country- or sector-specific. |
| Forward paths benefit from probabilities and price comparators. | Scenarios had no prior probabilities or Brent validation layer. | Scenario catalog adds editable probabilities and Brent bands; bands do not drive pricing. | Priors and bands remain analyst judgments. |
| Stress can move from Hormuz into Bab el-Mandeb and Suez. | Chokepoints were combined independently with no network propagation. | A lagged dependency matrix propagates stress; serial Red Sea exposures are grouped by maximum. | Shipment-level OD routing is still absent. |
| Physical sensing and quantitative modeling should update one another continuously. | Scenarios were fixed ex ante. | Optional sensor fusion blends observed physical severity into the daily path and updates opacity premium. | No live feed or Bayesian posterior update yet. |
| AIS-only indicators have selection bias when relevant ships stop declaring. | The model had no declared-versus-detected distinction. | SAR receives more physical-flow weight; SAR minus AIS becomes dark-activity opacity rather than missing supply. | Vessel association and false-positive logic are not implemented. |
| Ballast repositioning may lead but remains AIS-derived. | No leading physical indicator layer. | Ballast z-score informs forward risk but cannot override SAR physical passage. | Demonstration data are synthetic. |
| Radar can maintain a physical truth layer after AIS goes dark. | No confidence-weighted persistence mechanism. | Radar-wake persistence modifies fusion confidence. | No track-level persistence or image processing. |
| Fertilizer non-arrival can surface much later in yields. | Fertilizer used only a generic short lag. | A separate 150-day seasonal transmission queue links missed supply to later agricultural exposure. | Crop calendars and geography are aggregated. |
| Helium lacks the strategic stock buffer available to oil. | Inventory did not distinguish commercial and strategic stocks. | Commercial inventory and strategic reserve are separate; helium strategic reserve is zero. | Commercial inventory quantity and accessibility remain uncertain. |
| LNG, fertilizer, and helium share water but not impact timing. | Commodity-specific parameters existed but lacked enough mechanism separation. | Each commodity now has distinct demand speed, inventory, substitution, availability, and seasonal behavior. | Commodity subtypes and contract structures remain simplified. |

## Governance position

Private practitioner input informs hypotheses and architecture. Public factual claims and calibration anchors remain tied to the source register. The bundled sensor panel is synthetic and must not be represented as live, proprietary, or practitioner-supplied data.

## Version 0.3 calibration governance

Version 0.3 adds a non-driving calibration diagnostic. The deterministic grid
varies crude demand-price elasticity, demand adjustment days, commercial
inventory days, and scenario market-risk premium around the preserved baseline.
It reports band coverage, distance to the external Brent comparator, and the
assumption distance of each combination. A diagnostic rank is not an automatic
recommendation and never changes `commodities.csv` or `scenario_catalog.csv`.

Monte Carlo Brent coverage is calculated only for crude oil. Cross-commodity
`TOTAL` price fields are intentionally blank because the underlying units are
not comparable. Scenario priors also remain conditional analyst judgments;
weighted exposures cannot be summed across overlapping scenario paths.

## Version 0.4 structural market-balancing governance

Version 0.4 treats pipeline bypass, emergency stock releases, and external
non-chokepoint supply response as separate physical-market flows. The available
Saudi and UAE bypass capacity is anchored to EIA reporting, while ramp timing,
emergency-release accessibility, and external commodity response remain
editable scenario assumptions in `market_balancing.csv`.

Emergency stock releases reduce the strategic reserve state directly. The
remaining physical deficit may draw commercial inventory, but the model does
not automatically draw strategic stock again. This prevents reserve
double-counting between market-price moderation and shortage buffering.

The Brent decomposition reports the residual physical-gap contribution, base
scenario-risk premium, and sensor-opacity premium. If the price cap binds,
components are proportionally scaled so that they still sum exactly to the
reported price shock. Counterfactual paths preserve the same risk premium while
removing structural offsets or all structural and demand balancing.

The version 0.4 calibration grid replaces the commercial-inventory multiplier
with a structural-supply multiplier. A diagnostic rank still does not overwrite
any input file or make the Brent comparator a fitting target.

## Version 0.5 market segmentation and long-clock governance

Version 0.5 responds to four additional practitioner-informed questions without
using private discussion as public evidence.

| Question | Model response | Governance boundary |
|---|---|---|
| Can a global flat-price benchmark conceal acute stress in medium/heavy-sour crude? | A separate regional sour-complex proxy converts the compatible-barrel gap and route friction into a capped basis over the Brent proxy. | The path is an analyst proxy, not an Oman, Dubai, or Dated Brent forecast. |
| Can an import decline reflect a shift away from the benchmark market rather than lower consumption? | The model reports true demand reduction, segmented-channel shift, apparent benchmark withdrawal, and the price shock experienced by buyers with channel insulation. | The synthetic channel does not identify any buyer, sanctions program, or vessel. |
| Do reassigned heavy-sour barrels add supply? | Reassigned barrels reduce only the regional sour gap; the global physical balance is unchanged. | A regression test enforces this conservation rule. |
| How should undeclared activity be quantified? | Raw SAR-minus-AIS discrepancy is weighted by assumed detection recall, source confidence, backtest maturity, identity resolution, AIS staleness, and radar-wake persistence. | All bundled sensor performance fields remain synthetic until backtested against labeled detections. |
| How should ecological effects enter the model? | A named conditional branch runs separate desalination, fisheries/coastal-livelihood, and remediation lag states. | No ecological incident is inferred from disruption alone; exposure remains outside commodity totals. |

EIA public material supports the general claim that crude quality affects refinery
processing. NOAA incident and restoration material supports separating ecological
injury and long recovery horizons from immediate commodity prices. Exact grade,
channel, incident, timing, value-at-risk, and confidence parameters remain editable
analyst assumptions in `crude_market_structure.csv` and
`ecological_externalities.csv`.
