from saxonche import PySaxonProcessor


def xml_to_html(xml_text: str) -> str:
    xsl_file = "./assets/templates/isosts2html_standalone.xsl"
    with PySaxonProcessor(license=False) as proc:
        xslt_proc = proc.new_xslt30_processor()
        document = proc.parse_xml(xml_text=xml_text)
        executable = xslt_proc.compile_stylesheet(stylesheet_file=xsl_file)
        return executable.transform_to_string(xdm_node=document)
