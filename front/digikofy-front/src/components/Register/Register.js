import React, { useState } from "react"
import { useHistory } from "react-router-dom";

export default function Register() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const history = useHistory()

    /*
        Function called when submitting form. Check if email field or password field are not empty
        If empty then do nothing else call the API endpoing /register with the email and password given in the body
        After check the result and if the status code is 409 which means that an account with the same email already exists then 
        it will show an alert to inform the user
    */
    const onRegister = async (e) => {
        e.preventDefault()
        console.log(`Email : ${email} and Password : ${password}`)

        if(email.length === 0 || password.length === 0) return;
        
        try {
            
            const res = await fetch(
                "https://digikofy-front-back.herokuapp.com/api/register",
                { 
                    method : "POST",
                    headers: {
                        "Content-Type": "application/json"
                      },
                    body : JSON.stringify({email, password})
                })
            
            if(!res.ok && res.status === 409) {
                alert("Account with this email already exists")
                return;
            }

            alert("Account created successfully")

            history.push("/login")
            
        } catch (error) {
            console.log("Something went wrong => ", error)
        }
        
    }
    return (
        <div>
            <div>Register</div>
            <div>
                <form onSubmit={onRegister}>
                    <label>Email : </label>
                    <input placeholder="Input your email here" type="email" value={email} onChange={(e) => {setEmail(e.target.value)}}/>
                    <label>Password : </label>
                    <input placeholder="Input your password here" type="password" value={password} onChange={(e) => {setPassword(e.target.value)}}/>
                    <button>OK</button>
                </form>
            </div>
        </div>
    )
}