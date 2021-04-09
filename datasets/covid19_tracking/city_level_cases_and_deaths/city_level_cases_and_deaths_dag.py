# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from airflow import DAG
from airflow.contrib.operators import gcs_to_bq, gcs_to_gcs
from airflow.operators import bash_operator

default_args = {
    "owner": "Google",
    "depends_on_past": False,
    "start_date": "2021-03-01",
}


with DAG(
    dag_id="covid19_tracking.city_level_cases_and_deaths",
    default_args=default_args,
    max_active_runs=1,
    schedule_interval="@once",
    catchup=False,
    default_view="graph",
) as dag:

    # Task to copy full data for city-level cases and deaths from COVID-19 Tracking Project to GCS
    download_raw_csv_file = bash_operator.BashOperator(
        task_id="download_raw_csv_file",
        bash_command="mkdir -p $airflow_data_folder/covid19_tracking/city_level_cases_and_deaths/{{ ds }}\ncurl -o $airflow_data_folder/covid19_tracking/city_level_cases_and_deaths/{{ ds }}/raw-data.csv -L $csv_source_url\n",
        env={
            "csv_source_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRg-dB5Pjt-zN38BZNoCdOk_RJ_MyYFAl3QIkK5fKSddUy44DUgJwZuhjCz8KPMpiFKRwhoIwfs0NbZ/pub?gid=0&single=true&output=csv",
            "airflow_data_folder": "{{ var.json.shared.airflow_data_folder }}",
        },
    )

    # Run the custom/csv_transform.py script to process the raw CSV contents into a BigQuery friendly format
    process_raw_csv_file = bash_operator.BashOperator(
        task_id="process_raw_csv_file",
        bash_command="SOURCE_CSV=$airflow_home/data/$dataset/$pipeline/{{ ds }}/raw-data.csv TARGET_CSV=$airflow_home/data/$dataset/$pipeline/{{ ds }}/data.csv python $airflow_home/dags/$dataset/$pipeline/custom/csv_transform.py\n",
        env={
            "airflow_home": "{{ var.json.shared.airflow_home }}",
            "dataset": "covid19_tracking",
            "pipeline": "city_level_cases_and_deaths",
        },
    )

    # Task to load the data from Airflow data folder to BigQuery
    load_csv_file_to_bq_table = gcs_to_bq.GoogleCloudStorageToBigQueryOperator(
        task_id="load_csv_file_to_bq_table",
        bucket="{{ var.json.shared.composer_bucket }}",
        source_objects=[
            "data/covid19_tracking/city_level_cases_and_deaths/{{ ds }}/data.csv"
        ],
        source_format="CSV",
        destination_project_dataset_table="covid19_tracking.city_level_cases_and_deaths",
        skip_leading_rows=1,
        write_disposition="WRITE_TRUNCATE",
        schema_fields=[
            {"name": "date", "type": "DATE"},
            {"name": "state", "type": "STRING"},
            {"name": "location", "type": "STRING"},
            {"name": "city_or_county", "type": "STRING"},
            {"name": "cases_total", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_white", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_black", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_latinx", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_asian", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_aian", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_hnpi", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_multiracial", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_other", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_unknown", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "cases_ethnicity_hispanic", "type": "INTEGER", "mode": "NULLABLE"},
            {
                "name": "cases_ethnicity_nonhispanic",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {"name": "cases_ethnicity_unknown", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_total", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_white", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_black", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_latinx", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_asian", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_aian", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_hnpi", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_multiracial", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_other", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "deaths_unknown", "type": "INTEGER", "mode": "NULLABLE"},
            {
                "name": "deaths_ethnicity_hispanic",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "deaths_ethnicity_nonhispanic",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {"name": "deaths_ethnicity_unknown", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "case_fatality_rate", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "daily_new_cases", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "daily_percentincr_cases", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "weekly_new_cases", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "weekly_percentincr_cases", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "daily_new_deaths", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "daily_percentincr_deaths", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "weekly_new_deaths", "type": "INTEGER", "mode": "NULLABLE"},
            {
                "name": "weekly_percentincr_deaths",
                "type": "NUMERIC",
                "mode": "NULLABLE",
            },
        ],
    )

    # Task to archive the CSV file in the destination bucket
    archive_csv_file_to_destination_bucket = gcs_to_gcs.GoogleCloudStorageToGoogleCloudStorageOperator(
        task_id="archive_csv_file_to_destination_bucket",
        source_bucket="{{ var.json.shared.composer_bucket }}",
        source_object="data/covid19_tracking/city_level_cases_and_deaths/{{ ds }}/*",
        destination_bucket="{{ var.json.covid19_tracking.destination_bucket }}",
        destination_object="datasets/covid19_tracking/city_level_cases_and_deaths/{{ ds }}/",
        move_object=True,
    )

    download_raw_csv_file >> process_raw_csv_file
    process_raw_csv_file >> load_csv_file_to_bq_table
    load_csv_file_to_bq_table >> archive_csv_file_to_destination_bucket
