import { MDBCard, MDBCardBody, MDBCardTitle } from "mdb-react-ui-kit";

function BigTile({ title, subtitle, children, className, reference }) {
  return (
    <MDBCard className="my-5 px-5">
      <MDBCardTitle className="h2 text-center mt-3 mb-0" style={{fontWeight: 600}}>
        {title}
      </MDBCardTitle>
        <small className="text-center">
            {subtitle}
        </small>
      <MDBCardBody className={className} ref={reference}>
        {children}
      </MDBCardBody>
    </MDBCard>
  );
}

export default BigTile;