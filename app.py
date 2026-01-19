import os
from PIL import Image
import gradio as gr
import create_map_poster as cmp


def apply_color_overrides(theme_data, overrides):
    for key, value in overrides.items():
        if value:
            theme_data[key] = value
    return theme_data


def generate_poster(
    city,
    country,
    theme,
    distance,
    show_roads,
    show_water,
    show_parks,
    show_gradients,
    parallel_fetch,
    bg,
    text,
    gradient_color,
    water,
    parks,
    road_motorway,
    road_primary,
    road_secondary,
    road_tertiary,
    road_residential,
    road_default,
    progress=gr.Progress(),
):
    city = (city or "").strip()
    country = (country or "").strip()

    if not city or not country:
        raise gr.Error("Please provide both city and country.")

    theme_data = cmp.load_theme(theme)
    overrides = {
        "bg": bg,
        "text": text,
        "gradient_color": gradient_color,
        "water": water,
        "parks": parks,
        "road_motorway": road_motorway,
        "road_primary": road_primary,
        "road_secondary": road_secondary,
        "road_tertiary": road_tertiary,
        "road_residential": road_residential,
        "road_default": road_default,
    }
    cmp.THEME = apply_color_overrides(theme_data, overrides)
    coords = cmp.get_coordinates(city, country)
    output_file = cmp.generate_output_filename(city, theme)
    cmp.create_poster(
        city,
        country,
        coords,
        distance,
        output_file,
        show_water=show_water,
        show_parks=show_parks,
        show_roads=show_roads,
        show_gradients=show_gradients,
        parallel_fetch=parallel_fetch,
        progress_cb=progress,
    )

    output_path = os.path.abspath(output_file)
    img = Image.open(output_path)
    img.load()
    return img, output_path


def build_ui():
    themes = cmp.get_available_themes()
    if not themes:
        themes = ["feature_based"]

    with gr.Blocks(title="City Map Poster Generator") as demo:
        gr.Markdown("# City Map Poster Generator")
        gr.Markdown("Generate minimalist map posters for any city.")

        with gr.Row():
            with gr.Column(scale=1):
                city = gr.Textbox(label="City", placeholder="e.g., Tokyo")
                country = gr.Textbox(label="Country", placeholder="e.g., Japan")
                theme = gr.Dropdown(choices=themes, value=themes[0], label="Theme")
                distance = gr.Slider(
                    minimum=4000,
                    maximum=30000,
                    value=29000,
                    step=500,
                    label="Distance (meters)",
                )
                with gr.Accordion("Layers", open=True):
                    show_roads = gr.Checkbox(value=True, label="Show roads")
                    show_water = gr.Checkbox(value=True, label="Show water")
                    show_parks = gr.Checkbox(value=True, label="Show parks")
                    show_gradients = gr.Checkbox(value=True, label="Show gradients")
                    parallel_fetch = gr.Checkbox(
                        value=False,
                        label="Parallel downloads (may be unreliable)",
                    )

                with gr.Accordion("Color overrides", open=False):
                    bg = gr.ColorPicker(label="Background", value=None)
                    text = gr.ColorPicker(label="Text", value=None)
                    gradient_color = gr.ColorPicker(label="Gradient", value=None)
                    water = gr.ColorPicker(label="Water", value=None)
                    parks = gr.ColorPicker(label="Parks", value=None)
                    road_motorway = gr.ColorPicker(label="Roads: motorway", value=None)
                    road_primary = gr.ColorPicker(label="Roads: primary", value=None)
                    road_secondary = gr.ColorPicker(label="Roads: secondary", value=None)
                    road_tertiary = gr.ColorPicker(label="Roads: tertiary", value=None)
                    road_residential = gr.ColorPicker(label="Roads: residential", value=None)
                    road_default = gr.ColorPicker(label="Roads: default", value=None)

                submit = gr.Button("Generate Poster", variant="primary")

            with gr.Column(scale=1):
                image = gr.Image(
                    label="Poster Preview",
                    type="pil",
                    show_download_button=True,
                )
                download = gr.File(label="Download")

        submit.click(
            fn=generate_poster,
            inputs=[
                city,
                country,
                theme,
                distance,
                show_roads,
                show_water,
                show_parks,
                show_gradients,
                parallel_fetch,
                bg,
                text,
                gradient_color,
                water,
                parks,
                road_motorway,
                road_primary,
                road_secondary,
                road_tertiary,
                road_residential,
                road_default,
            ],
            outputs=[image, download],
        )

    return demo.queue()


if __name__ == "__main__":
    build_ui().launch()
