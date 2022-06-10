export default Spinner = (props) => {
    const Spin = () => (<div className="lds-ellipsis mx-auto"><div></div><div></div><div></div><div></div></div>);

    return props.center ? (
        <div className="mx-auto d-flex">
            <Spin />
        </div>
    ) : <Spin />;
}