{%- if obj.display %}
{% if sphinx_version >= (2, 1) %}

..
  {{ obj.__dict__ }}
  {{ obj.args }}

.. py:method:: {{ obj.short_name }}({{ obj.args }}) {% if obj.return_annotation %} -> {{ obj.return_annotation }} {% endif %}

{% else %}
.. {{ obj.method_type }}:: {{ obj.short_name }}({{ obj.args }})
{% endif %}

   {% if obj.properties|length > 0 %}
   .. rst-class:: prop
   {{ obj.properties|join(' ') }}
   {% endif %}

   {% if obj.docstring %}
   {{ obj.docstring|prepare_docstring|indent(3) }}
   {% endif %}
{% endif %}
