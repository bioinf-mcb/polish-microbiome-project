import logging
from rest_framework.views import APIView
from rest_framework.response import Response

import altair as alt
from altair import datum
import pandas as pd
from altair_saver import save
from io import StringIO
import json
from .utils.assembling_the_data import map_id_to_run
from django.db import connections

logger = logging.getLogger(__name__)
logger.info("Starting the view")

class PatientListView(APIView):
    def get(self, request, *args, **kwargs):
        def _try_parse(x):
            try:
                return "Alive" if int(x)==2 else "Dead"
            except (ValueError, TypeError):
                return "?"

        samples_df = map_id_to_run()


        redcap_db = connections['redcap']

        qry = """select record, 
                            MAX(IF(field_name='patient_id', CAST(value as UNSIGNED), NULL)) as patient_id,
                            MAX(IF(field_name='age', CAST(value as UNSIGNED), NULL)) as age,
                            MAX(IF(field_name='obesity', CAST(value as UNSIGNED), NULL)) as obesity,
                            MAX(IF(field_name='death', value, NULL)) as death,
                            MAX(IF(field_name='is_antibiotic', CAST(value as UNSIGNED), NULL)) as took_antibiotic
                            FROM redcap_data
                            GROUP BY record"""

        data = pd.read_sql(sql=qry, con=redcap_db)
        data["death"] = data["death"].apply(_try_parse)
        data["obesity"] = data["obesity"].apply(lambda x: "Obese" if x==1 else "No")
        data["took_antibiotic"] = data["took_antibiotic"].apply(lambda x: "Yes" if x==1 else x)
        data["took_antibiotic"] = data["took_antibiotic"].apply(lambda x: "No" if x==0 else x)
        data['samples'] = data['patient_id'].apply(lambda x: (samples_df['patient_id']==str(x)).sum())
        data = data.fillna("?")

        return Response({ 
            "data": data.sort_values(by=['patient_id']).to_dict('records')
        })


class ChartView(APIView):
    def get(self, request, patient_id):
        width = request.GET.get('width', None)
        if width == 'undefined' or width is None:
            width = 'container'
        else:
            width = int(float(width))
        logger.warn(f"Width: {width}")
        
        samples_df = map_id_to_run()
        samples_df = samples_df[samples_df['patient_id']==patient_id]

        clinical_df = pd.read_csv('/data/clinical_data.csv')
        drug_df = pd.read_csv('/data/drug_info.csv').dropna()
        drug_df = drug_df[drug_df['patient_id']==patient_id]
        logger.warn(drug_df)
        
        # We are interested only in the results that have some significance i.r.t covid
        important_results = ['ALT', 'AST', 'Białko ostrej fazy - CRP', 'D-dimer', 'Ferrytyna', 'Interleukina 6', 'LDH (L)']
        filtered_clinical_df = clinical_df.loc[clinical_df['profile'].isin(important_results), :]

        filtered_clinical_df.loc[:, 'patient_id'] = filtered_clinical_df['patient_id'].astype(int)
        filtered_clinical_df = filtered_clinical_df.reset_index(drop=True)

        # Altair library forces us to mash everything into one dataframe
        for idx, row in samples_df.iterrows():
            new_row = {i: None for i in filtered_clinical_df.columns}
            new_row['redcap_repeat_instrument'] = 'sample'
            try:
                dtime = row['sample_date']
                new_row['date_of_test'] = pd.Timestamp(dtime)
            except:
                continue
                
            new_row['order_no'] = row['run']
            new_row['patient_id'] = row['patient_id']
            
            filtered_clinical_df.loc[len(filtered_clinical_df), :] = new_row

        filtered_clinical_df = filtered_clinical_df[filtered_clinical_df['patient_id'] == patient_id]
        filtered_clinical_df = filtered_clinical_df[filtered_clinical_df['date_of_test']!='date_of_test']
        filtered_clinical_df['date_of_test'] = pd.to_datetime(filtered_clinical_df['date_of_test'].values)

        samples = alt.Chart(filtered_clinical_df).mark_rule(strokeDash=[5]).encode(
                        alt.X('date_of_test:T', timeUnit='yearmonthdate', title='Date'),
                        alt.Color('order_no', title='value', legend=None),
                        alt.Tooltip('order_no')
        ).transform_filter(datum.redcap_repeat_instrument=='sample').properties(width=width)

        def get_chart_for_profile(profile):
            patient_result = alt.Chart(filtered_clinical_df).mark_line(interpolate='cardinal', point=True).encode(
                                    alt.X('date_of_test:T', timeUnit='yearmonthdate', title='Date'),
                                    alt.Y('value:Q', title='value'),
                                    alt.Tooltip('value:Q')
                                ).transform_filter(datum.profile==profile).properties(width=width)

            patient_norm = alt.Chart(filtered_clinical_df).mark_area(opacity=0.1, color='green').encode(
                                    alt.X('date_of_test:T', title='Date'),
                                    alt.Y('norm_lower:Q', title='value'),
                                    alt.Y2('norm_upper:Q')
                                ).transform_filter(datum.profile==profile).properties(width=width)
            
            return (patient_norm + samples + patient_result).properties(title=profile, width=width)

        chart = get_chart_for_profile('ALT')
        for i in filtered_clinical_df.profile.unique()[1:]:
            if i is not None:
                chart = chart & get_chart_for_profile(i)

        if len(drug_df) > 0:
            medicine_chart = alt.Chart(drug_df).mark_bar().encode(
                x=alt.X('drug_start_date:T', timeUnit='yearmonthdate', title='Date'),
                x2=alt.X2('drug_end_date:T', timeUnit='yearmonthdate', title='Date'),
                color=alt.Color("is_antibiotic:N"),
                tooltip=alt.condition(alt.datum.is_antibiotic==1, alt.value("Antibiotic"), alt.value("Not antibiotic")),
                y=alt.Y('drug_name', title='Drug name')).properties(width=width) + samples

            chart = (medicine_chart & chart)
        
        chart = chart.configure(background='#FFFFFF00').resolve_scale(x="shared")
        out = StringIO()
        save(chart, out, fmt="json")
        res = json.loads(out.getvalue())
        logger.warn(res.keys())

        return Response(res)
