// Generate barebones navbar using mdb-react-ui-kit
import { useState } from 'react';
import {
    MDBNavbar, MDBNavbarBrand, MDBNavbarNav, MDBNavbarItem, MDBNavbarLink, MDBNavbarToggler, MDBCollapse, MDBIcon, MDBContainer, MDBRow, MDBTypography
} from "mdb-react-ui-kit";
import { StyleSheet, css } from 'aphrodite';
const logo = require("../../../public/happy_microbe.jpg");

const Navbar = (props) => {
    const toggleNav = () => setShowNav(!showNav);
    console.log(logo);
    return (
        <MDBNavbar bgColor='light' expand='lg' className='d-flex flex-column p-0'>
            <div className="w-100">
                <MDBContainer className="w-auto">
                    <MDBNavbarBrand>
                        <MDBNavbarBrand>
                            <MDBTypography
                                tag="h1"
                                className={"font-weight-bold text-uppercase m-0 " + css(styles.navbarBrand)}
                                nogutter
                            >
                                <img src={logo} alt="logo" className="mr-2 py-0" height={"64px"} />
                                {"Project overview"}
                            </MDBTypography>
                        </MDBNavbarBrand>
                        <MDBNavbarToggler
                            type='button'
                            aria-expanded='false'
                            aria-label='Toggle navigation'
                            onClick={toggleNav}
                        ></MDBNavbarToggler>
                    </MDBNavbarBrand>
                </MDBContainer>
            </div>
            <div className={"w-100 " + css(styles.navbarMenu)}>
                <MDBContainer fluid>
                    <MDBNavbarNav className="justify-content-center">
                        <MDBNavbarItem>
                            <MDBNavbarLink href="#!">Project Summary</MDBNavbarLink>
                        </MDBNavbarItem>
                        <MDBNavbarItem>
                            <MDBNavbarLink href="#!">Patients' Inspector</MDBNavbarLink>
                        </MDBNavbarItem>
                    </MDBNavbarNav>
                </MDBContainer>
            </div>
        </MDBNavbar >
    );
};

export default Navbar;

const styles = StyleSheet.create({
    navbarBrand: {
        fontSize: "1.5rem",
        fontWeight: "bold",
        color: "black"
    },
    navbarMenu: {
        backgroundColor: "#113C4A",
        color: "white"
    },
    
});