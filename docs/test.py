#para ejecutar, en la terminal: streamlit run test.py



import streamlit as st

st. title("Test del Sensor Virtual Inteligente")


st.write("Hola, este es un test para el sensor virtual inteligente")

with st.form("my_form"):
    name = st.text_input("Nombre")
    age = st.number_input("Edad", min_value=0, max_value=120)
    submit = st.form_submit_button("Enviar")

    #import pickle
    # with open("model.pkl", "rb") as f:
    #     model = pickle.load(f)


# y haora metemos las varibles par que el modelo prega, si son a manos seria como antes: st.text_input.....


# podemos subir csv....


#st.dataframe(df)....


button = st.button("Predecir")


if button:
    st.success("¡Predicción realizada con éxito!")
    st.write(f"Nombre: {name}")
    
#pred = model.predict([dsfad.csv])  # Aquí se usaría el modelo para hacer la predicción con los datos ingresados


