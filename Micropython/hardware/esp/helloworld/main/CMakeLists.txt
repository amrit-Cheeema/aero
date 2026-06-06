idf_component_register(SRCS "main.c" "init.c"
                    INCLUDE_DIRS "."
                    REQUIRES bt
                    REQUIRES nvs_flash
                    )
