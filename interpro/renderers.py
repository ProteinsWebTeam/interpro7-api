from rest_framework import renderers
import io
import csv

fields_to_exclude = ["entry_annotations"]


def flatDict(original, output=None, prefix=None):
    if output is None:
        output = {}
    for key, value in original.items():
        p_key = key if prefix is None else "{}__{}".format(prefix, key)
        if isinstance(value, dict):
            flatDict(value, output, prefix=p_key)
        else:
            output[p_key] = value

    return output


class TSVRenderer(renderers.BaseRenderer):
    media_type = "text/tab-separated-values"
    format = "tsv"

    def render(self, data, media_type=None, renderer_context=None):
        objs = None
        if "metadata" in data:
            objs = [data["metadata"]]
            # writer.writeheader(data["metadata"])
        elif "results" in data:
            # writer.writeheader(data["results"][0]["metadata"])
            objs = [item["metadata"] for item in data["results"]]
        elif isinstance(data, dict):
            objs = [flatDict(data)]

        output = io.StringIO()
        if objs is not None:
            writer = csv.DictWriter(
                output,
                fieldnames=[k for k in sorted(objs[0]) if k not in fields_to_exclude],
                extrasaction="ignore",
                delimiter="\t",
                quoting=csv.QUOTE_NONNUMERIC,
            )
            writer.writeheader()
            writer.writerows(objs)

        return output.getvalue()
