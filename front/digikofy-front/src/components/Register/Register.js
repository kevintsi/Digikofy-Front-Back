import React, { useState } from "react"

export default function Register() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")

    const onRegister = async (e) => {
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
            console.log(`Result : ${res.json()}`)    
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