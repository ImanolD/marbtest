import replicate
import streamlit as st
import requests
import zipfile
import io
from utils import icon
from streamlit_image_select import image_select

# UI configurations
st.set_page_config(page_title="MARB - Crea con Nosotros",
                   page_icon=":robot_face:",
                   layout="wide")
st.image("https://cdn.shopify.com/s/files/1/0569/4295/2534/files/marbnegro.png?v=1704953829")
st.title("Tu Creatividad en el Mundo MARB")
st.caption("Te presentamos 'Crea con MARB', donde tu inspiración se convierte en realidad. Envía tus diseños y utiliza nuestra tecnología de visualización 3D para ver tus muebles en diferentes ambientes. Transforma tus ideas en innovaciones con MARB.")
option = st.selectbox('¿Qué tipo de mueble estás imaginando?', ('Arturito', 'Espejo', 'Mesa', 'Cabecera', 'Comoda', 'Otro'))
details = st.text_input('¿Qué características especiales tiene este mueble?')
location = st.text_input('¿Donde quieres ubicar este mueble?')
submitted = st.button("Generar", type="primary")
prompt = ''
# prompt = st.chat_input("¿Qué características especiales tiene este mueble y donde lo quieres ubicar?")


# API Tokens and endpoints from `.streamlit/secrets.toml` file
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_ENDPOINTSTABILITY = st.secrets["REPLICATE_MODEL_ENDPOINTSTABILITY"]

# Resources text, link, and logo
replicate_text = "Regresar a la página de MARB"
replicate_link = "https://replicate.com/stability-ai/sdxl"
replicate_logo = "https://storage.googleapis.com/llama2_release/Screen%20Shot%202023-07-21%20at%2012.34.05%20PM.png"

# Placeholders for images and gallery
generated_images_placeholder = st.empty()
gallery_placeholder = st.empty()


def configure_sidebar() -> None:
    """
    Setup and display the sidebar elements.

    This function configures the sidebar of the Streamlit application, 
    including the form for user inputs and the resources section.
    """
    with st.sidebar:
        st.image("https://cdn.shopify.com/s/files/1/0569/4295/2534/files/marbnegro.png?v=1704953829")
        with st.form("my_form"):
            # st.info("**¿Quieres configurar algo?**")
            with st.expander("**¿Quieres configurar algo?**"):
                # Advanced Settings (for the curious minds!)
                # width = st.number_input("Ancho de la imagen", value=1024)
                # height = st.number_input("Alto de la imagen", value=1024)
                # num_outputs = st.slider(
                #     "Número de imagenes a crear", value=1, min_value=1, max_value=4)
                # scheduler = st.selectbox('Scheduler', ('DDIM', 'DPMSolverMultistep', 'HeunDiscrete',
                #                                        'KarrasDPM', 'K_EULER_ANCESTRAL', 'K_EULER', 'PNDM'))
                # num_inference_steps = st.slider(
                #     "Number of denoising steps", value=50, min_value=1, max_value=500)
                # guidance_scale = st.slider(
                #     "Scale for classifier-free guidance", value=7.5, min_value=1.0, max_value=50.0, step=0.1)
                # prompt_strength = st.slider(
                #     "Prompt strength when using img2img/inpaint(1.0 corresponds to full destruction of infomation in image)", value=0.8, max_value=1.0, step=0.1)
                # refine = st.selectbox(
                #     "Select refine style to use (left out the other 2)", ("expert_ensemble_refiner", "None"))
                # high_noise_frac = st.slider(
                #     "Fraction of noise to use for `expert_ensemble_refiner`", value=0.8, max_value=1.0, step=0.1)
                
                width = 1024
                height = 1024
                num_outputs = 2
                scheduler = 'DDIM'
                num_inference_steps = 50
                guidance_scale = 7.50
                prompt_strength = 0.80
                refine = "expert_ensemble_refiner"
                high_noise_frac = 0.80
                

            # prompt = st.text_area(
            #     ":orange[**Enter prompt: start typing, Shakespeare ✍🏾**]",
            #     value="An astronaut riding a rainbow unicorn, cinematic, dramatic")
            # negative_prompt = st.text_area(":orange[**Party poopers you don't want in image? 🙅🏽‍♂️**]",
            #                                value="the absolute worst quality, distorted features",
            #                                help="This is a negative prompt, basically type what you don't want to see in the generated image")
            
            negative_prompt = "the absolute worst wuality, distorted features, no wooden furniture in the image"

            # The Big Red "Submit" Button!
            # submitted = st.form_submit_button(
            #     "Submit", type="primary", use_container_width=True)

        # Credits and resources
        st.divider()
        st.markdown(
            ":orange[**Resources:**]  \n"
            f"<img src='{replicate_logo}' style='height: 1em'> [{replicate_text}]({replicate_link})",
            unsafe_allow_html=True
        )
        # st.markdown(
        #     """
        #     ---
        #     Follow me on:

        #     𝕏 → [@tonykipkemboi](https://twitter.com/tonykipkemboi)

        #     LinkedIn → [Tony Kipkemboi](https://www.linkedin.com/in/tonykipkemboi)

        #     """
        # )

        return submitted, width, height, num_outputs, scheduler, num_inference_steps, guidance_scale, prompt_strength, refine, high_noise_frac, prompt, negative_prompt


def main_page(submitted: bool, width: int, height: int, num_outputs: int,
              scheduler: str, num_inference_steps: int, guidance_scale: float,
              prompt_strength: float, refine: str, high_noise_frac: float,
              prompt: str, negative_prompt: str) -> None:
    """Main page layout and logic for generating images.

    Args:
        submitted (bool): Flag indicating whether the form has been submitted.
        width (int): Width of the output image.
        height (int): Height of the output image.
        num_outputs (int): Number of images to output.
        scheduler (str): Scheduler type for the model.
        num_inference_steps (int): Number of denoising steps.
        guidance_scale (float): Scale for classifier-free guidance.
        prompt_strength (float): Prompt strength when using img2img/inpaint.
        refine (str): Refine style to use.
        high_noise_frac (float): Fraction of noise to use for `expert_ensemble_refiner`.
        prompt (str): Text prompt for the image generation.
        negative_prompt (str): Text prompt for elements to avoid in the image.
    """
    if submitted:
        with st.status('🤖 Creando imagenes con IA...', expanded=True) as status:
            st.write("⚙️ Iniciando Modelos de MARB")
            try:
                # Only call the API if the "Submit" button was pressed
                if submitted:
                    prompt = 'Crear una imagen realista de un mueble de 80 cm de ancho y 1.60m de alto. '+details+' . El mueble es hueco, tiene postes verticales, una mesa con cajón a la mitad de la altura. Añadir pequeñas incrustaciones o acentos de color turquesa en puntos de unión en los postes verticales. La madera debe reflejar un acabado satinado, resaltando el trabajo de carpintería fino y la calidad del mueble, el cual es funcional y decorativo. Este mueble esta ubicado en '+location
                    # Calling the replicate API to get the image
                    with generated_images_placeholder.container():
                        all_images = []  # List to store all generated images
                        output = replicate.run(
                            REPLICATE_MODEL_ENDPOINTSTABILITY,
                            input={
                                "prompt": prompt,
                                "width": width,
                                "height": height,
                                "num_outputs": num_outputs,
                                "scheduler": scheduler,
                                "num_inference_steps": num_inference_steps,
                                "guidance_scale": guidance_scale,
                                "prompt_stregth": prompt_strength,
                                "refine": refine,
                                "high_noise_frac": high_noise_frac
                            }
                        )
                        if output:
                            st.toast(
                                'Your image has been generated!', icon='😍')
                            # Save generated image to session state
                            st.session_state.generated_image = output

                            # Displaying the image
                            for image in st.session_state.generated_image:
                                with st.container():
                                    st.image(image, caption="Imagen Generada 🎈",
                                             use_column_width=True)
                                    # Add image to the list
                                    all_images.append(image)

                                    response = requests.get(image)
                        # Save all generated images to session state
                        st.session_state.all_images = all_images

                        # Create a BytesIO object
                        zip_io = io.BytesIO()

                        # Download option for each image
                        with zipfile.ZipFile(zip_io, 'w') as zipf:
                            for i, image in enumerate(st.session_state.all_images):
                                response = requests.get(image)
                                if response.status_code == 200:
                                    image_data = response.content
                                    # Write each image to the zip file with a name
                                    zipf.writestr(
                                        f"output_file_{i+1}.png", image_data)
                                else:
                                    st.error(
                                        f"Failed to fetch image {i+1} from {image}. Error code: {response.status_code}", icon="🚨")
                        # Create a download button for the zip file
                        st.download_button(
                            ":red[**Descargar Imagenes**]", data=zip_io.getvalue(), file_name="output_files.zip", mime="application/zip", use_container_width=True)
                        st.text(prompt)
                status.update(label="✅ Imagenes generadas!",
                              state="complete", expanded=False)
            except Exception as e:
                print(e)
                st.error(f'Encountered an error: {e}', icon="🚨")

    # If not submitted, chill here 🍹
    else:
        pass

    # Gallery display for inspo
    # with gallery_placeholder.container():
    #     img = image_select(
    #         label="Like what you see? Right-click and save! It's not stealing if we're sharing! 😉",
    #         images=[
    #             "gallery/farmer_sunset.png", "gallery/astro_on_unicorn.png",
    #             "gallery/friends.png", "gallery/wizard.png", "gallery/puppy.png",
    #             "gallery/cheetah.png", "gallery/viking.png",
    #         ],
    #         captions=["A farmer tilling a farm with a tractor during sunset, cinematic, dramatic",
    #                   "An astronaut riding a rainbow unicorn, cinematic, dramatic",
    #                   "A group of friends laughing and dancing at a music festival, joyful atmosphere, 35mm film photography",
    #                   "A wizard casting a spell, intense magical energy glowing from his hands, extremely detailed fantasy illustration",
    #                   "A cute puppy playing in a field of flowers, shallow depth of field, Canon photography",
    #                   "A cheetah mother nurses her cubs in the tall grass of the Serengeti. The early morning sun beams down through the grass. National Geographic photography by Frans Lanting",
    #                   "A close-up portrait of a bearded viking warrior in a horned helmet. He stares intensely into the distance while holding a battle axe. Dramatic mood lighting, digital oil painting",
    #                   ],
    #         use_container_width=True
    #     )


def main():
    """
    Main function to run the Streamlit application.

    This function initializes the sidebar configuration and the main page layout.
    It retrieves the user inputs from the sidebar, and passes them to the main page function.
    The main page function then generates images based on these inputs.
    """
    submitted, width, height, num_outputs, scheduler, num_inference_steps, guidance_scale, prompt_strength, refine, high_noise_frac, prompt, negative_prompt = configure_sidebar()
    main_page(submitted, width, height, num_outputs, scheduler, num_inference_steps,
              guidance_scale, prompt_strength, refine, high_noise_frac, prompt, negative_prompt)


if __name__ == "__main__":
    main()
