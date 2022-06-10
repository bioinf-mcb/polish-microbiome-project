// Basic container with header and footer using mdb-react-ui-kit
//
// Language: javascript
// Path: frontend/src/Components/Container/Container.jsx
import { MDBContainer, MDBRow, MDBCol } from 'mdb-react-ui-kit';
import Navbar from './Navbar';
import { Outlet } from 'react-router-dom';

const MainContainer = ({ children }) => {
  return (
    <>
      <Navbar />
      <MDBContainer>
        <MDBRow>
          <MDBCol>
            <Outlet />
          </MDBCol>
        </MDBRow>
      </MDBContainer>
    </>
  );
};

export default MainContainer;