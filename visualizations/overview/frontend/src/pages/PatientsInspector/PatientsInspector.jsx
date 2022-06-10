import React, { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import BigTile from "../../Components/BigTile";
import DataTable from 'react-data-table-component';
import { StyleSheet, css } from "aphrodite";
import Spinner from "../../Components/Spinner";
import { MDBCol, MDBRow } from "mdb-react-ui-kit";
import * as ReactDOM from 'react-dom';

function PatientsInspector() {
    const { patient_id } = useParams();
    const [clickedRow, setClickedRow] = React.useState(patient_id);

    const navigate = useNavigate();
    const [ready, setReady] = React.useState(false);

    const canvasContainer = React.useRef({ current: {} });
    const canvasParent = React.useRef({ current: {} });

    useEffect(() => {
        setReady(false);
        var patientToGet = clickedRow;

        if (clickedRow)
            vegaEmbed("#graph", `http://localhost:8000/chart/${clickedRow}?width=${canvasContainer.current.offsetWidth * 0.6}`, { mode: "vega-lite" })
                .then(result => {
                    setReady(true);
                });
    }, [clickedRow]);

    return (
        <MDBRow>
            <div className="flex items-center justify-center">
                <h1 className="mx-auto mt-5" style={{ width: "fit-content", fontWeight: "bold" }}>Patients' Inspector</h1>
            </div>
            <MDBCol xl="5" l="5" md="12">
                <BigTile title="Table of patients" subtitle="">
                    <React.StrictMode>
                        <PatientsTable highlighted={patient_id} callback={(value) => {
                            navigate(`/inspector/${value}`, { replace: true });
                            setClickedRow(value);
                        }} />
                    </React.StrictMode>
                </BigTile>
            </MDBCol>
            <MDBCol xl="7" l="7" md="12">
                <BigTile reference={canvasParent} title="Clinical data" subtitle={"Patient " + clickedRow}>
                    {!ready && <Spinner center />}
                    <div id='graph' ref={canvasContainer} style={{ width: "100%" }}>
                    </div>
                </BigTile>
            </MDBCol>
        </MDBRow>
    )
}

function PatientsTable({ callback, highlighted }) {
    const [data, setData] = React.useState([]);
    const [ready, setReady] = React.useState(false);
    console.log(rowStyle.clicked)

    useEffect(() => {
        fetch('http://localhost:8000/patient_list')
            .then(response => response.json())
            .then(data => {
                setData(data.data);
                setReady(true);
            })
    }, []);

    if (!ready) {
        return <Spinner center />
    }

    return (
        <DataTable
            columns={DATA_COLUMNS}
            data={data}
            pagination
            conditionalRowStyles={[
                {
                    when: row => row.patient_id == highlighted,
                    style: rowStyle.clicked._definition
                }
            ]}
            onRowClicked={(rowData, rowMeta) => {
                callback(rowData.patient_id);
            }}
        />
    )
}

export default PatientsInspector;


// Constants
const rowStyle = StyleSheet.create({
    clicked: {
        backgroundColor: "#ff914d",
    },
    unclicked: {
        backgroundColor: "#fff",
    }
});

const DATA_COLUMNS = [
    {
        name: 'Patient ID',
        selector: row => row.patient_id,
    },
    {
        name: 'Age',
        selector: row => row.age,
    },
    {
        name: 'Obesity',
        selector: row => row.obesity,
    },
    {
        name: 'Death',
        selector: row => row.death,
    },
    {
        name: "Took antibiotic?",
        selector: row => row.took_antibiotic,
    },
    {
        name: "Samples",
        selector: row => row.samples,
    }
];