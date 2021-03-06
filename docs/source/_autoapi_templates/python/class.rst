{% if obj.display %}
.. py:{{ obj.type }}:: {{ obj.short_name }}{% if obj.args %}({{ obj.args }}){% endif %}


    .. rst-class:: full-class-path

      {{ obj.id }}

    {% if obj.docstring %}
    {{ obj.docstring|prepare_docstring|indent(4) }}
    {% endif %}

    {% if obj.bases %}
    {% if "show-inheritance" in autoapi_options %}
    Bases: {% for base in obj.bases %}:class:`{{ base }}`{% if not loop.last %}, {% endif %}{% endfor %}
    {% endif %}


    {% if "show-inheritance-diagram" in autoapi_options and obj.bases != ["object"] %}
    .. autoapi-inheritance-diagram:: {{ obj.obj["full_name"] }}
    :parts: 1
    {% if "private-members" in autoapi_options %}
    :private-bases:
    {% endif %}
    {% endif %}
    {% endif %}
    {% if "inherited-members" in autoapi_options %}
    {% set visible_classes = obj.classes|selectattr("display")|list %}
    {% else %}
    {% set visible_classes = obj.classes|rejectattr("inherited")|selectattr("display")|list %}
    {% endif %}
    {% for klass in visible_classes %}
    {{ klass.rendered|indent(4) }}
    {% endfor %}
    {% if "inherited-members" in autoapi_options %}
    {% set visible_attributes = obj.attributes|selectattr("display")|list %}
    {% else %}
    {% set visible_attributes = obj.attributes | rejectattr("inherited") | selectattr("display") | list %}
    {% endif %}
    {% set metadata = visible_attributes | selectattr("obj.annotation", "eq", "MetadataKey") | list %}
    {% set visible_attributes = visible_attributes | rejectattr("obj.annotation", "eq", "MetadataKey") | list %}
    {% if metadata %}
    :raw-html:`<div class='section-metadata'>`
    Record metadata supported:

    {% for meta in metadata %}
    {{ meta.rendered|indent(4) }}
    {% endfor %}
    :raw-html:`</div>`
    {% endif %}

    {% for attribute in visible_attributes %}
    {{ attribute.rendered|indent(4) }}
    {% endfor %}
    {% if "inherited-members" in autoapi_options %}
    {% set visible_methods = obj.methods|selectattr("display")|list %}
    {% else %}
    {% set visible_methods = obj.methods|rejectattr("inherited")|selectattr("display")|list %}
    {% endif %}
    {% for method in visible_methods %}
    {{ method.rendered|indent(4) }}
    {% endfor %}
{% endif %}