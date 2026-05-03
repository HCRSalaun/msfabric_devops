from msfabric_devops import set_semantic_model_parameters

set_semantic_model_parameters(
    "output",                                   # relative to project root
    {
        "Param_Brand":   "X",
        "Param_Billing": "dev",
        "Param_Source":  "prod",
    },
    fail_if_not_found=False,
)
print("Parameters updated successfully.")
