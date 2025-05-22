# democracytracker
This is a tool to accelerate the Collection and validation of pro-democracy activities.  It supports the dataviz 
https://public.tableau.com/app/profile/tom.hirata/viz/2025Pro-DemocracyProtests/Dashboard1

1. Review records submitted by activists with information (metadata) about protests on a date at a specific location
2. Validate that submitted URL includes sufficient evidence that the protest occurred (photo of people at an identifiable location, and a date of the event
3. Provide optional classification of the protest to enable feature updates in the dataviz
4. Allow the validator to clean up dates and places when the URL disagrees with the user-created metadata

## Setup
`democracytracker` depends on `pandas`, `streamlit`, and `openpyxl`.

`watchdog` is an optional dependency that `streamlit` says improves performance.

Dependency management using `pipenv` is recommended.

1. Install `pipenv` [according to the instructions](https://pipenv.pypa.io/en/latest/installation.html)
2. Clone the repository: `git clone git@github.com:devtmh/democracytracker.git`
3. Navigate to the repository folder and activate the virtual environment: `pipenv activate`
4. Install dependencies: `pipenv install`

## Usage
Run `streamlit run protest_validation.py`, and a browser window will open
with the validation interface.
