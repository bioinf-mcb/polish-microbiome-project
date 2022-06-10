import { MDBCard, MDBCardBody, MDBCardTitle, MDBInput } from "mdb-react-ui-kit";
import { useCallback, useState } from "react";

async function getBackendResult(value) {
  var endpoint = process.env.ENDPOINT + "/char_count?text=";
  var res = await fetch(endpoint+value)
    .then(response => response.json())
    .then(data => data.count);

  return res;
}

function PlaceholderPage() {
  const [result, setResult] = useState(null);
    
  return (
    <MDBCard className="my-5 px-5">
      <MDBCardTitle className="h1 text-center mt-5 mb-0 font-weight-bold">
        Placeholder Page
      </MDBCardTitle>
      <small className="text-center">
        Server address: {process.env.ENDPOINT}
      </small>
      <MDBCardBody>
        <p className="text-center w-responsive mx-auto mb-5">
          Lorem ipsum dolor sit amet, consectetur adipisicing elit. Fugit,
          error amet numquam iure provident voluptate esse quasi, veritatis
          totam voluptas nostrum quisquam eum porro a pariatur veniam.
        </p>
        <MDBInput
          label="Enter text to count characters"
          type="text"
          onChange={async value => {
            var res = await getBackendResult(value.target.value);
            console.log(res);
            setResult(res);
          }}
        />
        <p className="text-center w-responsive mx-auto mb-3 mt-2">
          {result ? result : null}
        </p>
      </MDBCardBody>
    </MDBCard>
  );
}

export default PlaceholderPage;