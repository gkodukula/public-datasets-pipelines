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
    dag_id="covid19_tracking.state_level_cumulative_long_term_care",
    default_args=default_args,
    max_active_runs=1,
    schedule_interval="@once",
    catchup=False,
    default_view="graph",
) as dag:

    # Task to copy data from HTTP source to GCS or Airflow home dir
    download_raw_csv_file = bash_operator.BashOperator(
        task_id="download_raw_csv_file",
        bash_command="mkdir -p $airflow_home/data/covid19_tracking/state_level_cumulative_long_term_care\ncurl -o $airflow_home/data/covid19_tracking/state_level_cumulative_long_term_care/raw-cumulative-data-{{ ds }}.csv -L $csv_source_url\n",
        env={
            "csv_source_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRa9HnmEl83YXHfbgSPpt0fJe4SyuYLc0GuBAglF4yMYaoKSPRCyXASaWXMrTu1WEYp1oeJZIYHpj7t/pub?gid=467018747&single=true&output=csv",
            "airflow_home": "{{ var.json.shared.airflow_home }}",
        },
    )

    # Run the custom/csv_transform.py script to process the raw CSV contents into a BigQuery friendly format
    process_raw_csv_file = bash_operator.BashOperator(
        task_id="process_raw_csv_file",
        bash_command="SOURCE_CSV=$airflow_home/data/$dataset/$pipeline/raw-cumulative-data-{{ ds }}.csv TARGET_CSV=$airflow_home/data/$dataset/$pipeline/cumulative-data-{{ ds }}.csv python $airflow_home/dags/$dataset/$pipeline/custom/csv_transform.py\n",
        env={
            "airflow_home": "{{ var.json.shared.airflow_home }}",
            "dataset": "covid19_tracking",
            "pipeline": "state_level_cumulative_long_term_care",
        },
    )

    # Task to load the CSV from the pipeline's data folder to BigQuery
    load_csv_file_to_bq_table = gcs_to_bq.GoogleCloudStorageToBigQueryOperator(
        task_id="load_csv_file_to_bq_table",
        bucket="{{ var.json.shared.composer_bucket }}",
        source_objects=[
            "data/covid19_tracking/state_level_cumulative_long_term_care/cumulative-data-{{ ds }}.csv"
        ],
        source_format="CSV",
        destination_project_dataset_table="covid19_tracking.state_level_cumulative_long_term_care",
        skip_leading_rows=1,
        write_disposition="WRITE_TRUNCATE",
        schema_fields=[
            {"name": "date", "type": "DATE"},
            {"name": "state", "type": "STRING"},
            {"name": "data_timestamp", "type": "STRING", "mode": "NULLABLE"},
            {"name": "data_set", "type": "STRING"},
            {
                "name": "nursing_homes_resident_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_probable_resident_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_resident_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_probable_resident_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_probable_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_probable_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_resident_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_probable_res_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_resident_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_probable_res_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "nursing_homes_number_of_facilities_with_outbreak",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_resident_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_probable_resident_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_resident_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_probable_resident_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_probable_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_probable_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_resident_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_probable_res_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_resident_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_probable_res_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "assisted_living_number_of_facilities_with_outbreak",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_resident_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_probable_resident_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_resident_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_probable_resident_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_probable_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_probable_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_resident_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_probable_res_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_resident_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_probable_res_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "uncategorized_ltc_facilities_number_of_facilities_with_outbreak",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_resident_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_probable_resident_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_resident_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_probable_resident_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_probable_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_probable_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_resident_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_probable_res_staff_positives",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_resident_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_probable_res_staff_deaths",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
            {
                "name": "other_care_facilities_number_of_facilities_with_outbreak",
                "type": "INTEGER",
                "mode": "NULLABLE",
            },
        ],
    )

    # Task to archive the CSV file in the destination bucket
    archive_csv_file_to_destination_bucket = gcs_to_gcs.GoogleCloudStorageToGoogleCloudStorageOperator(
        task_id="archive_csv_file_to_destination_bucket",
        source_bucket="{{ var.json.shared.composer_bucket }}",
        source_object="data/covid19_tracking/state_level_cumulative_long_term_care/*-data-{{ ds }}.csv",
        destination_bucket="{{ var.json.covid19_tracking.destination_bucket }}",
        destination_object="datasets/covid19_tracking/state_level_cumulative_long_term_care/{{ ds }}/",
        move_object=True,
    )

    download_raw_csv_file >> process_raw_csv_file
    process_raw_csv_file >> load_csv_file_to_bq_table
    load_csv_file_to_bq_table >> archive_csv_file_to_destination_bucket
