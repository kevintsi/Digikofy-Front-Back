import React from "react"

export default function Coffee({coffee}) {
    return (
        <div>
            <div><a href={`/detail/${coffee.id}`}>{coffee.name}</a></div>
        </div>
    )
}