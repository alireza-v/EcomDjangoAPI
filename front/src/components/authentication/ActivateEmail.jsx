import axios from "axios";
import { useEffect, useState } from "react";
import { useParams,useNavigate } from "react-router-dom";

function ActivateAccount() {
        const { uid, token } = useParams();
        const [message, setMessage] = useState("");
        const navigate = useNavigate();

        useEffect(() => {
                document.title = "Activate email";
        }, []);

        useEffect(() => {
                axios
                        .get(`http://localhost:9000/api/auth/activate/${uid}/${token}/`)
                        .then(() => {
                                setMessage("✅ Account activated successfully!");
                                setTimeout(() => {
                                        navigate("/");
                                }, 2000);
                        })
                        .catch((err) => {
                                setMessage("❌ Activation failed.");
                                console.error(err);
                        });
        }, [uid, token]);


        return <div>{message}</div>;
};
export default ActivateAccount;
