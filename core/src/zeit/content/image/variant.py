import UserDict
import copy
import grokcore.component as grok
import zeit.cms.content.sources
import zeit.content.image.interfaces
import zeit.edit.body
import zope.schema


class Variants(grok.Adapter, UserDict.DictMixin):

    grok.context(zeit.content.image.interfaces.IImageGroup)
    grok.implements(zeit.content.image.interfaces.IVariants)

    def __init__(self, context):
        super(Variants, self).__init__(context)
        self.__parent__ = context

    def __getitem__(self, key):
        if key in self.context.variants:
            variant = Variant(id=key, **self.context.variants[key])
            config = VARIANT_SOURCE.factory.find(self.context, key)
            self._copy_missing_fields(config, variant)
        else:
            variant = VARIANT_SOURCE.factory.find(self.context, key)
            self._copy_missing_fields(self.default_variant, variant)
        variant.__parent__ = self
        return variant

    def _copy_missing_fields(self, source, target):
        for key in zope.schema.getFieldNames(
                zeit.content.image.interfaces.IVariant):
            if hasattr(target, key):
                continue
            if hasattr(source, key):
                setattr(target, key, getattr(source, key))

    def keys(self):
        keys = [x.id for x in VARIANT_SOURCE(self.context)]
        for key in self.context.variants.keys():
            if key not in keys:
                keys.append(key)
        return keys

    @property
    def default_variant(self):
        if Variant.DEFAULT_NAME in self.context.variants:
            default = self[Variant.DEFAULT_NAME]
        else:
            default = VARIANT_SOURCE.factory.find(
                self.context, Variant.DEFAULT_NAME)
        return default


class Variant(object):

    DEFAULT_NAME = 'default'
    interface = zeit.content.image.interfaces.IVariant

    grok.implements(interface)

    def __init__(self, **kw):
        """Set attributes that are part of the Schema and convert their type"""
        fields = zope.schema.getFields(self.interface)
        for key, value in kw.items():
            if key not in fields:
                continue  # ignore attributes that aren't part of the schema
            value = fields[key].fromUnicode(unicode(value))
            setattr(self, key, value)

    @property
    def ratio(self):
        xratio, yratio = self.aspect_ratio.split(':')
        return float(xratio) / float(yratio)

    @property
    def is_default(self):
        return self.id == self.DEFAULT_NAME


class VariantSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.image'
    config_url = 'variant-source'

    def getTitle(self, context, value):
        return value.id

    def getToken(self, context, value):
        return value.id

    def getValues(self, context):
        tree = self._get_tree()
        result = []
        for node in tree.getchildren():
            if not self.isAvailable(node, context):
                continue

            if node.countchildren() == 0:
                # If there are no children, create a Variant from parent node
                result.append(Variant(**node.attrib))

            for size in node.getchildren():
                # Create Variant for each given size
                result.append(Variant(**self._merge_attributes(
                    node.attrib, size.attrib)))
        return result

    def find(self, context, id):
        for value in self.getValues(context):
            if value.id == id:
                return value
        raise KeyError(id)

    def _merge_attributes(self, parent_attr, child_attr):
        """Merge attributes from parent with those from child.

        Attributes from child are more specific and therefore may overwrite
        attributes from parent. Create the child `id` via concatenation, since
        it should be unique among variants and respects the parent / child
        hierarchy.

        """
        result = copy.copy(parent_attr)
        result.update(child_attr)

        if 'id' in parent_attr and 'id' in child_attr:
            result['id'] = '{}-{}'.format(parent_attr['id'], child_attr['id'])

        return result


VARIANT_SOURCE = VariantSource()


class VariantsTraverser(zeit.edit.body.Traverser):

    grok.context(zeit.content.image.interfaces.IImageGroup)
    body_name = 'variants'
    body_interface = zeit.content.image.interfaces.IVariants


@grok.adapter(zeit.content.image.interfaces.IVariants)
@grok.implementer(zeit.content.image.interfaces.IImageGroup)
def imagegroup_for_variants(context):
    return zeit.content.image.interfaces.IImageGroup(context.__parent__)


@grok.adapter(zeit.content.image.interfaces.IVariant)
@grok.implementer(zeit.content.image.interfaces.IImageGroup)
def imagegroup_for_variant(context):
    return zeit.content.image.interfaces.IImageGroup(context.__parent__)
