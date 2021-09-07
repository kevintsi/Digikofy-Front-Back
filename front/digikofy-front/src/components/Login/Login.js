import React, { useState} from "react"
import { useHistory } from "react-router-dom";

export default function Login() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const history = useHistory()
    
    const onLogin = async (e) => {
        e.preventDefault()
        console.log(`Email : ${email} and Password : ${password}`)
        try {
            const res = await fetch(
                "http://localhost:8000/login",
                { 
                    method : "POST",
                    headers: {
                        "Content-Type": "application/json"
                      },
                    body : JSON.stringify({email, password})
                })
            console.log("Result : ", await res.json())

            const data = await res.json()

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