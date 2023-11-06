class Profile:
    """A Profile is a specification that constrains, extends, combines, or provides guidance or explanation about
    the usage of other specifications.

    This definition includes what are sometimes called "application profiles", "metadata application profiles", or
    "metadata profiles". In this document, "data profile" and these other variants are all referred to as just
    "profiles".

    This definition of Profiles is from The Profiles Vocabulary: https://www.w3.org/TR/dx-prof/ and objects created
    using this class are intended for use as prof:Profile instances.
    """

    def __init__(
        self,
        uri,
        label,
        comment,
        mediatypes,
        default_mediatype,
        languages=None,
        default_language="en",
        is_profile_of=None,
    ):
        """
        Constructor

        :param uri: The namespace URI for the *profile* view.
        :type uri: str
        :param label: The human-readable label for the Profile.
        :type label: str
        :param comment: A description of the Profile.
        :type comment: str
        :param mediatypes: The list of IANA MediaTypes that this Profile supports.
        :type mediatypes: list
        :param default_mediatype: The default MediaType that this Profile is delivered in.
        :type default_mediatype: str
        :param languages: A list of languages this Profile supports. Identified by ISO 639-1 2-letter language codes.
        :type languages: list
        :param default_language: The default language, by default it is 'en': English.
        :type default_language: str
        :param is_profile_of: A list of URIs (strings) that this Profile is a Profile of
        :type is_profile_of: list
        """
        self.uri = uri
        self.label = label
        self.comment = comment
        self.mediatypes = mediatypes
        self.default_mediatype = default_mediatype
        self.languages = languages if languages is not None else ["en"]
        self.default_language = default_language
        self.is_profile_of = is_profile_of

    def __str__(self):
        return self.uri


RDF_MEDIA_TYPES = [
    "text/turtle",
    "application/rdf+xml",
    "application/ld+json",
    "text/n3",
    "application/n-triples",
]


HTML_MEDIA_TYPE = "text/html"


VOC_PUB_PROFILE_46 = Profile(
    "https://w3id.org/profile/vocpub/4.6",
    "Vocabulary Publication Profile v4.6",
    "SKOS ConceptSchemes, Collections & Concepts as well as additional Dublin Core Terms & schema.org "
    "annotation properties to be used to publish vocabularies.",
    RDF_MEDIA_TYPES + [HTML_MEDIA_TYPE, "text/markdown"],
    HTML_MEDIA_TYPE,
    languages=["en"],
    default_language="en",
    is_profile_of=["https://www.w3.org/TR/skos-reference/"],
)


PROFILES = {"vocpub-46": VOC_PUB_PROFILE_46}
