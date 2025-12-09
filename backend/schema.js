const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
    fname: String,
    lname: String, 
    email: {
        type: String,
        required: true,
        unique: true,
    },
    password: String
})

const movieSchema = new mongoose.Schema({
    movie_name: String,
    movie_id:{
        type: Number,
        required: true,
        unique: true

    },
    movie_description: String, 
    has_watched: Boolean,
    rating: Number,

})

const messages = new mongoose.Schema({
    timestamp: {
        type: Date,
        default: Date.now,
    },
    content: String,
    role: ["user", "model"],
    convo_id: {
        type: Number,
        required: true,
        unique: true
    }

})

const convo = new mongoose.Schema({
    user_email:String,
    convo_id: {
        type: Number,
        required: true,
        unique: true
    },
    messages: [messages]
})