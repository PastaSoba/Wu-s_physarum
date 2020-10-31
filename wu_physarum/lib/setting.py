MODEL_PARAM = {
    "width": 200,
    "height": 200,
    "density": 0.5,
    "seed": 13573,
}

PHYSARUM_PARAM = {
    "sensor_arm_length": 7,  # The distance between sensor and its body
    "depT": 5,               # The quantity of trail deposited by an agent
    "WT": 0.4,               # The weight of trail value sensed by an agent's
                             # factor
    "WN": 0.6,               # The weight of chemo-nutrient value sensed by an
                             # agent's factor (1-WT)
    "RT": 15,                # If the motion counter is greater than RT,
                             # the reproduction is triggered
    "ET": -10,               # If the motion counter is less than ET,
                             # the elimination is triggered
}

LATTICECELL_PARAM = {
    "dampT": 0.1,            # Diffusion damping factor of trail
    "filterT_width": 3,      # The width of mean filter for trail
    "filterT_height": 3,     # The height of mean filter for trail

    "CN": 10,                # The chemo-nutrient concentration of each Node
    "dampN": 0.2,            # Diffusion damping factor of chemo-nutrient
    "filterN_width": 5,      # The width of mean filter for chemo-nutrient
    "filterN_height": 5,     # The height of mean filter for chemo-nutrient
}
