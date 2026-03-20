import React, { useState } from "react";
import { View, Text, TextInput, Button, StyleSheet } from "react-native";

export default function App() {
  const [hour, setHour] = useState("");
  const [usage, setUsage] = useState("");
  const [result, setResult] = useState("");

  const predict = async () => {
    const res = await fetch("http://YOUR-IP:5000/predict", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({
        hour,
        usage,
        mood: "neutral"
      })
    });

    const data = await res.json();
    setResult(data.message + "\n" + data.suggestion);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Life Pattern AI</Text>

      <TextInput
        placeholder="Hour"
        style={styles.input}
        onChangeText={setHour}
      />

      <TextInput
        placeholder="Usage"
        style={styles.input}
        onChangeText={setUsage}
      />

      <Button title="Analyze" onPress={predict} />

      <Text style={styles.result}>{result}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container:{flex:1,justifyContent:"center",padding:20},
  input:{backgroundColor:"#fff",padding:10,margin:10},
  title:{fontSize:24,marginBottom:20},
  result:{marginTop:20}
});
