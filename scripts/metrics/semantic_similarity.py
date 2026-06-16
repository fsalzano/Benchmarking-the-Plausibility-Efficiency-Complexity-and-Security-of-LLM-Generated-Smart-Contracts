from smartembed import SmartEmbed
se = SmartEmbed()


def get_similarity(gt, generated):
    gpt_gen_function = 'pragma solidity ^0.8.0; \n\n' + str(generated)
    gt_function = 'pragma solidity ^0.8.0; \n\n' + str(gt)

    vec1 = se.get_vector(gt_function)
    vec2 = se.get_vector(gpt_gen_function)
    print("similarity")

    similarity = se.get_similarity(vec1, vec2)
    return similarity

