import React, { useState} from "react"
import { useHistory } from "react-router-dom";

export default function Login() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const history = useHistory()
    
    /*
        Function called when submitting form. Check if email field or password field are not empty
        If empty then do nothing
    */
    const onLogin = async (e) => {
        e.preventDefault()
        console.log(`Email : ${email} and Password : ${password}`)

        if(email.length === 0 || password.length === 0) return;

        try {
            const res = await fetch(
                "https://digikofy-front-back.herokuapp.com/api/login",
                { 
                    method : "POST",
                    headers: {
                        "Content-Type": "application/json"
                      },
                    body : JSON.stringify({email, password})
                })

            const data = await res.json()


            console.log("Result : ", data)

            localStorage.setItem("token", data.idToken)

            history.push("/home")
                
        } catch (error) {
            console.log("Something went wrong => ", error)
        }
    }
    return (
        <div>
            <div>Login</div>
            <div>
                <form onSubmit={onLogin}>
                    <label>Email : </label>
                    <input placeholder="Input your email here" type="email" value={email} onChange={(e) => {setEmail(e.target.value)}}/>
                    <label>Password : </label>
                    <input placeholder="Input your password here" type="password" value={password} onChange={(e) => {setPassword(e.target.value)}}/>
                    <button type="submit">Log in</button>
                </form>
            </div>
        </div>
    )
}