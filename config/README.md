# Frozen experiment design

experiment.json records the submitted-design configuration instantiated for the original run. scenarios.json fixes all 24 starts and split assignments. Their contents were relocated without changes. load_design() validates both before execution; supported model constants are fixed rather than silently overridden. A separate new-run snapshot records any development episode budget.
