# Copyright 2022 Google LLC
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
from airflow.operators import bash
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.providers.google.cloud.transfers import gcs_to_bigquery

default_args = {
    "owner": "Google",
    "depends_on_past": False,
    "start_date": "2021-03-01",
}


with DAG(
    dag_id="fec.individuals_2016",
    default_args=default_args,
    max_active_runs=1,
    schedule_interval="@daily",
    catchup=False,
    default_view="graph",
) as dag:

    # Task to copy `individuals` to gcs
    download_zip_file = bash.BashOperator(
        task_id="download_zip_file",
        bash_command='mkdir -p $data_dir/individuals\ncurl -o $data_dir/individuals/indiv16.zip -L $fec\nunzip $data_dir/individuals/indiv16.zip -d $data_dir/individuals/\nawk \u0027NR%7000000==1{x="/home/airflow/gcs/data/fec/individuals/F"++i;}{print \u003e x}\u0027  $data_dir/individuals/itcont.txt\n',
        env={
            "data_dir": "/home/airflow/gcs/data/fec",
            "fec": "https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads/2016/indiv16.zip",
        },
    )

    # Run CSV transform within kubernetes pod
    individuals_2016_transform_csv_1 = kubernetes_pod.KubernetesPodOperator(
        task_id="individuals_2016_transform_csv_1",
        startup_timeout_seconds=600,
        name="individuals_2016",
        namespace="composer",
        service_account_name="datasets",
        image_pull_policy="Always",
        image="{{ var.json.fec.container_registry.run_csv_transform_kub_2 }}",
        env_vars={
            "SOURCE_GCS_BUCKET": "{{ var.value.composer_bucket }}",
            "SOURCE_GCS_OBJECT": "data/fec/individuals/F1.txt",
            "SOURCE_FILE": "files/F1.txt",
            "TARGET_FILE": "files/data_output.csv",
            "TARGET_GCS_BUCKET": "{{ var.value.composer_bucket }}",
            "TARGET_GCS_PATH": "data/fec/individuals/data_output_1.csv",
            "TABLE_NAME": "individuals_2016",
            "CSV_HEADERS": '["cmte_id","amndt_ind","rpt_tp","transaction_pgi","image_num","transaction_tp","entity_tp","name","city","state", "zip_code","employer","occupation","transaction_dt","transaction_amt","other_id","tran_id","file_num", "memo_cd","memo_text","sub_id"]',
            "RENAME_MAPPINGS": '{"0":"cmte_id","1":"amndt_ind","2":"rpt_tp","3":"transaction_pgi","4":"image_num","5":"transaction_tp", "6":"entity_tp","7":"name","8":"city","9":"state","10":"zip_code","11":"employer", "12":"occupation","13":"transaction_dt","14":"transaction_amt","15":"other_id","16":"tran_id", "17":"file_num","18":"memo_cd","19":"memo_text","20":"sub_id"}',
        },
        resources={
            "request_memory": "5G",
            "request_cpu": "1",
            "request_ephemeral_storage": "10G",
        },
    )

    # Task to load CSV data to a BigQuery table
    load_individuals_2016_1_to_bq = gcs_to_bigquery.GCSToBigQueryOperator(
        task_id="load_individuals_2016_1_to_bq",
        bucket="{{ var.value.composer_bucket }}",
        source_objects=["data/fec/individuals/data_output_1.csv"],
        source_format="CSV",
        destination_project_dataset_table="fec.individuals_2016",
        skip_leading_rows=1,
        allow_quoted_newlines=True,
        write_disposition="WRITE_APPEND",
        schema_fields=[
            {
                "name": "cmte_id",
                "type": "string",
                "description": "Filer Identification Number",
                "mode": "nullable",
            },
            {
                "name": "amndt_ind",
                "type": "string",
                "description": "Amendment Indicator",
                "mode": "nullable",
            },
            {
                "name": "rpt_tp",
                "type": "string",
                "description": "Report Type",
                "mode": "nullable",
            },
            {
                "name": "transaction_pgi",
                "type": "string",
                "description": "Primary-General Indicator",
                "mode": "nullable",
            },
            {
                "name": "image_num",
                "type": "integer",
                "description": "Image Number",
                "mode": "nullable",
            },
            {
                "name": "transaction_tp",
                "type": "string",
                "description": "Transaction Type",
                "mode": "nullable",
            },
            {
                "name": "entity_tp",
                "type": "string",
                "description": "Entity Type",
                "mode": "nullable",
            },
            {
                "name": "name",
                "type": "string",
                "description": "Contributor/Lender/Transfer Name",
                "mode": "nullable",
            },
            {
                "name": "city",
                "type": "string",
                "description": "City/Town",
                "mode": "nullable",
            },
            {
                "name": "state",
                "type": "string",
                "description": "State",
                "mode": "nullable",
            },
            {
                "name": "zip_code",
                "type": "string",
                "description": "Zip Code",
                "mode": "nullable",
            },
            {
                "name": "employer",
                "type": "string",
                "description": "Employer",
                "mode": "nullable",
            },
            {
                "name": "occupation",
                "type": "string",
                "description": "Occupation",
                "mode": "nullable",
            },
            {
                "name": "transaction_dt",
                "type": "date",
                "description": "Transaction Date(MMDDYYYY)",
                "mode": "nullable",
            },
            {
                "name": "transaction_amt",
                "type": "float",
                "description": "Transaction Amount",
                "mode": "nullable",
            },
            {
                "name": "other_id",
                "type": "string",
                "description": "Other Identification Number",
                "mode": "nullable",
            },
            {
                "name": "tran_id",
                "type": "string",
                "description": "Transaction ID",
                "mode": "nullable",
            },
            {
                "name": "file_num",
                "type": "integer",
                "description": "File Number / Report ID",
                "mode": "nullable",
            },
            {
                "name": "memo_cd",
                "type": "string",
                "description": "Memo Code",
                "mode": "nullable",
            },
            {
                "name": "memo_text",
                "type": "string",
                "description": "Memo Text",
                "mode": "nullable",
            },
            {
                "name": "sub_id",
                "type": "integer",
                "description": "FEC Record Number",
                "mode": "required",
            },
        ],
    )

    # Run CSV transform within kubernetes pod
    individuals_2016_transform_csv_2 = kubernetes_pod.KubernetesPodOperator(
        task_id="individuals_2016_transform_csv_2",
        startup_timeout_seconds=600,
        name="individuals_2016",
        namespace="composer",
        service_account_name="datasets",
        image_pull_policy="Always",
        image="{{ var.json.fec.container_registry.run_csv_transform_kub_2 }}",
        env_vars={
            "SOURCE_GCS_BUCKET": "{{ var.value.composer_bucket }}",
            "SOURCE_GCS_OBJECT": "data/fec/individuals/F2.txt",
            "SOURCE_FILE": "files/F2.txt",
            "TARGET_FILE": "files/data_output.csv",
            "TARGET_GCS_BUCKET": "{{ var.value.composer_bucket }}",
            "TARGET_GCS_PATH": "data/fec/individuals/data_output_2.csv",
            "TABLE_NAME": "individuals_2016",
            "CSV_HEADERS": '["cmte_id","amndt_ind","rpt_tp","transaction_pgi","image_num","transaction_tp","entity_tp","name","city","state", "zip_code","employer","occupation","transaction_dt","transaction_amt","other_id","tran_id","file_num", "memo_cd","memo_text","sub_id"]',
            "RENAME_MAPPINGS": '{"0":"cmte_id","1":"amndt_ind","2":"rpt_tp","3":"transaction_pgi","4":"image_num","5":"transaction_tp", "6":"entity_tp","7":"name","8":"city","9":"state","10":"zip_code","11":"employer", "12":"occupation","13":"transaction_dt","14":"transaction_amt","15":"other_id","16":"tran_id", "17":"file_num","18":"memo_cd","19":"memo_text","20":"sub_id"}',
        },
    )

    # Task to load CSV data to a BigQuery table
    load_individuals_2016_2_to_bq = gcs_to_bigquery.GCSToBigQueryOperator(
        task_id="load_individuals_2016_2_to_bq",
        bucket="{{ var.value.composer_bucket }}",
        source_objects=["data/fec/individuals/data_output_2.csv"],
        source_format="CSV",
        destination_project_dataset_table="fec.individuals_2016",
        skip_leading_rows=1,
        allow_quoted_newlines=True,
        write_disposition="WRITE_APPEND",
        schema_fields=[
            {
                "name": "cmte_id",
                "type": "string",
                "description": "Filer Identification Number",
                "mode": "nullable",
            },
            {
                "name": "amndt_ind",
                "type": "string",
                "description": "Amendment Indicator",
                "mode": "nullable",
            },
            {
                "name": "rpt_tp",
                "type": "string",
                "description": "Report Type",
                "mode": "nullable",
            },
            {
                "name": "transaction_pgi",
                "type": "string",
                "description": "Primary-General Indicator",
                "mode": "nullable",
            },
            {
                "name": "image_num",
                "type": "integer",
                "description": "Image Number",
                "mode": "nullable",
            },
            {
                "name": "transaction_tp",
                "type": "string",
                "description": "Transaction Type",
                "mode": "nullable",
            },
            {
                "name": "entity_tp",
                "type": "string",
                "description": "Entity Type",
                "mode": "nullable",
            },
            {
                "name": "name",
                "type": "string",
                "description": "Contributor/Lender/Transfer Name",
                "mode": "nullable",
            },
            {
                "name": "city",
                "type": "string",
                "description": "City/Town",
                "mode": "nullable",
            },
            {
                "name": "state",
                "type": "string",
                "description": "State",
                "mode": "nullable",
            },
            {
                "name": "zip_code",
                "type": "string",
                "description": "Zip Code",
                "mode": "nullable",
            },
            {
                "name": "employer",
                "type": "string",
                "description": "Employer",
                "mode": "nullable",
            },
            {
                "name": "occupation",
                "type": "string",
                "description": "Occupation",
                "mode": "nullable",
            },
            {
                "name": "transaction_dt",
                "type": "date",
                "description": "Transaction Date(MMDDYYYY)",
                "mode": "nullable",
            },
            {
                "name": "transaction_amt",
                "type": "float",
                "description": "Transaction Amount",
                "mode": "nullable",
            },
            {
                "name": "other_id",
                "type": "string",
                "description": "Other Identification Number",
                "mode": "nullable",
            },
            {
                "name": "tran_id",
                "type": "string",
                "description": "Transaction ID",
                "mode": "nullable",
            },
            {
                "name": "file_num",
                "type": "integer",
                "description": "File Number / Report ID",
                "mode": "nullable",
            },
            {
                "name": "memo_cd",
                "type": "string",
                "description": "Memo Code",
                "mode": "nullable",
            },
            {
                "name": "memo_text",
                "type": "string",
                "description": "Memo Text",
                "mode": "nullable",
            },
            {
                "name": "sub_id",
                "type": "integer",
                "description": "FEC Record Number",
                "mode": "required",
            },
        ],
    )

    # Run CSV transform within kubernetes pod
    individuals_2016_transform_csv_3 = kubernetes_pod.KubernetesPodOperator(
        task_id="individuals_2016_transform_csv_3",
        startup_timeout_seconds=600,
        name="individuals_2016",
        namespace="composer",
        service_account_name="datasets",
        image_pull_policy="Always",
        image="{{ var.json.fec.container_registry.run_csv_transform_kub_2 }}",
        env_vars={
            "SOURCE_GCS_BUCKET": "{{ var.value.composer_bucket }}",
            "SOURCE_GCS_OBJECT": "data/fec/individuals/F3.txt",
            "SOURCE_FILE": "files/F3.txt",
            "TARGET_FILE": "files/data_output.csv",
            "TARGET_GCS_BUCKET": "{{ var.value.composer_bucket }}",
            "TARGET_GCS_PATH": "data/fec/individuals/data_output_3.csv",
            "TABLE_NAME": "individuals_2016",
            "CSV_HEADERS": '["cmte_id","amndt_ind","rpt_tp","transaction_pgi","image_num","transaction_tp","entity_tp","name","city","state", "zip_code","employer","occupation","transaction_dt","transaction_amt","other_id","tran_id","file_num", "memo_cd","memo_text","sub_id"]',
            "RENAME_MAPPINGS": '{"0":"cmte_id","1":"amndt_ind","2":"rpt_tp","3":"transaction_pgi","4":"image_num","5":"transaction_tp", "6":"entity_tp","7":"name","8":"city","9":"state","10":"zip_code","11":"employer", "12":"occupation","13":"transaction_dt","14":"transaction_amt","15":"other_id","16":"tran_id", "17":"file_num","18":"memo_cd","19":"memo_text","20":"sub_id"}',
        },
        resources={
            "request_memory": "5G",
            "request_cpu": "1",
            "request_ephemeral_storage": "10G",
        },
    )

    # Task to load CSV data to a BigQuery table
    load_individuals_2016_3_to_bq = gcs_to_bigquery.GCSToBigQueryOperator(
        task_id="load_individuals_2016_3_to_bq",
        bucket="{{ var.value.composer_bucket }}",
        source_objects=["data/fec/individuals/data_output_3.csv"],
        source_format="CSV",
        destination_project_dataset_table="fec.individuals_2016",
        skip_leading_rows=1,
        allow_quoted_newlines=True,
        write_disposition="WRITE_APPEND",
        schema_fields=[
            {
                "name": "cmte_id",
                "type": "string",
                "description": "Filer Identification Number",
                "mode": "nullable",
            },
            {
                "name": "amndt_ind",
                "type": "string",
                "description": "Amendment Indicator",
                "mode": "nullable",
            },
            {
                "name": "rpt_tp",
                "type": "string",
                "description": "Report Type",
                "mode": "nullable",
            },
            {
                "name": "transaction_pgi",
                "type": "string",
                "description": "Primary-General Indicator",
                "mode": "nullable",
            },
            {
                "name": "image_num",
                "type": "integer",
                "description": "Image Number",
                "mode": "nullable",
            },
            {
                "name": "transaction_tp",
                "type": "string",
                "description": "Transaction Type",
                "mode": "nullable",
            },
            {
                "name": "entity_tp",
                "type": "string",
                "description": "Entity Type",
                "mode": "nullable",
            },
            {
                "name": "name",
                "type": "string",
                "description": "Contributor/Lender/Transfer Name",
                "mode": "nullable",
            },
            {
                "name": "city",
                "type": "string",
                "description": "City/Town",
                "mode": "nullable",
            },
            {
                "name": "state",
                "type": "string",
                "description": "State",
                "mode": "nullable",
            },
            {
                "name": "zip_code",
                "type": "string",
                "description": "Zip Code",
                "mode": "nullable",
            },
            {
                "name": "employer",
                "type": "string",
                "description": "Employer",
                "mode": "nullable",
            },
            {
                "name": "occupation",
                "type": "string",
                "description": "Occupation",
                "mode": "nullable",
            },
            {
                "name": "transaction_dt",
                "type": "date",
                "description": "Transaction Date(MMDDYYYY)",
                "mode": "nullable",
            },
            {
                "name": "transaction_amt",
                "type": "float",
                "description": "Transaction Amount",
                "mode": "nullable",
            },
            {
                "name": "other_id",
                "type": "string",
                "description": "Other Identification Number",
                "mode": "nullable",
            },
            {
                "name": "tran_id",
                "type": "string",
                "description": "Transaction ID",
                "mode": "nullable",
            },
            {
                "name": "file_num",
                "type": "integer",
                "description": "File Number / Report ID",
                "mode": "nullable",
            },
            {
                "name": "memo_cd",
                "type": "string",
                "description": "Memo Code",
                "mode": "nullable",
            },
            {
                "name": "memo_text",
                "type": "string",
                "description": "Memo Text",
                "mode": "nullable",
            },
            {
                "name": "sub_id",
                "type": "integer",
                "description": "FEC Record Number",
                "mode": "required",
            },
        ],
    )

    (
        download_zip_file
        >> individuals_2016_transform_csv_1
        >> load_individuals_2016_1_to_bq
        >> individuals_2016_transform_csv_2
        >> load_individuals_2016_2_to_bq
        >> individuals_2016_transform_csv_3
        >> load_individuals_2016_3_to_bq
    )
