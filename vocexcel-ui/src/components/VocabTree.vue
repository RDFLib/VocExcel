<script setup lang="ts">
import { ref } from 'vue'
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import Tree from 'primevue/tree'
import Toast from 'primevue/toast'
import ProgressSpinner from 'primevue/progressspinner'
import { useToast } from 'primevue/usetoast'
import { Parser, Store, DataFactory, NamedNode, BlankNode, Literal } from 'n3'
import { QueryEngine } from '@comunica/query-sparql-rdfjs'

type Node = NamedNode | BlankNode | Literal | null
interface TreeNode {
  key: string
  label: string
  children: TreeNode[]
}
const { namedNode } = DataFactory
const RDF_TYPE = namedNode('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
const SKOS_CONCEPT_SCHEME = namedNode('http://www.w3.org/2004/02/skos/core#ConceptScheme')
const SKOS_PREF_LABEL = namedNode('http://www.w3.org/2004/02/skos/core#prefLabel')
const SKOS_NARROWER = namedNode('http://www.w3.org/2004/02/skos/core#narrower')
const SKOS_TOP_CONCEPT_OF = namedNode('http://www.w3.org/2004/02/skos/core#topConceptOf')

const getOne = (s: Node, p: Node, o: Node): string | null => {
  const quads = store.getQuads(s, p, o, null)

  if (quads.length > 0) {
    const quad = quads[0]
    if (s === null) {
      return quad.subject.value
    } else if (p === null) {
      return quad.predicate.value
    } else {
      return quad.object.value
    }
  }

  return null
}

const getObject = (s: NamedNode, p: NamedNode): string | null => {
  return getOne(s, p, null)
}

const getChildren = (iri: string, parentNode: TreeNode) => {
  const label = getOne(namedNode(iri), SKOS_PREF_LABEL, null) || iri

  const node: TreeNode = {
    key: iri,
    label: `${label} (Concept)`,
    children: []
  }

  const narrowerConcepts = store.getObjects(namedNode(iri), SKOS_NARROWER, null)

  for (const narrowerConcept of narrowerConcepts) {
    getChildren(narrowerConcept.value, node)
  }

  parentNode.children.push(node)
}

const getBnodeDepth = (store: Store, node: Node, depth: number = 0, seen: BlankNode[] = []) => {
  if (node instanceof BlankNode || depth === 0) {
    const objects = store.getObjects(node, null, null)
    for (const o of objects) {
      if (o instanceof BlankNode && !seen.includes(o)) {
        seen.push(o)
        depth = getBnodeDepth(store, o, depth + 1, seen)
      }
    }
  }

  return depth
}

const getConvertedRdfValue = async (ntriplesValue: string) => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/format', {
      method: 'POST',
      headers: { 'Content-Type': 'application/n-triples' },
      body: ntriplesValue
    })
    return await response.text()
  } catch (error) {
    const errorMsg = 'Failed to load resource: Could not connect to the server.'
    console.error(error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMsg,
      life: 3000
    })
    return null
  }
}

const getConstructQuery = async (focusNodeIri: string, blankNodeDepth: number) => {
  try {
    const response = await fetch(
      `http://localhost:8000/api/v1/construct-query?focus_node_iri=${focusNodeIri}&depth=${blankNodeDepth}`
    )
    return await response.text()
  } catch (error) {
    let errorMsg = 'Failed to load resource: Could not connect to the server.'
    console.error(error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMsg,
      life: 3000
    })
    return null
  }
}

// Component logic
const props = defineProps<{ rdfTurtle: string }>()
const toast = useToast()
const queryEngine = new QueryEngine()
const selectedKey = ref()
const selectedNodeTurtleValue = ref('')
const isTurtleCodeLoading = ref(false)

const handleNodeSelectAsync = async (node: TreeNode) => {
  const bnodeDepth = getBnodeDepth(store, namedNode(node.key))
  const query = await getConstructQuery(node.key, bnodeDepth)

  if (query !== null) {
    try {
      const result = await queryEngine.query(query, {
        sources: [store]
      })
      const { data } = await queryEngine.resultToString(result, 'application/n-triples')

      let ntriplesValue = ''
      data.on('data', (chunk) => {
        ntriplesValue += chunk.toString()
      })

      data.on('end', async () => {
        const convertedValue = await getConvertedRdfValue(ntriplesValue)
        if (convertedValue !== null) {
          selectedNodeTurtleValue.value = convertedValue
        }
        isTurtleCodeLoading.value = false
      })

      data.on('error', (error) => {
        console.error(error)
        isTurtleCodeLoading.value = false
      })
    } catch (err) {
      console.error(err)
    }
  }
}

const handleNodeSelect = (node: any) => {
  selectedNodeTurtleValue.value = ''
  isTurtleCodeLoading.value = true
  handleNodeSelectAsync(node)
}

const handleNodeUnselect = () => {
  selectedNodeTurtleValue.value = ''
  isTurtleCodeLoading.value = false
}

const store = new Store()
const parser = new Parser()
const quads = parser.parse(props.rdfTurtle)
store.addQuads(quads)

const treeNodes = ref<TreeNode[]>([])
const conceptSchemeIri = getOne(null, RDF_TYPE, SKOS_CONCEPT_SCHEME)

if (conceptSchemeIri !== null) {
  const conceptSchemeLabel = getObject(namedNode(conceptSchemeIri), SKOS_PREF_LABEL)

  const conceptSchemeNode: TreeNode = {
    key: conceptSchemeIri,
    label: `${conceptSchemeLabel} (Concept Scheme)`,
    children: []
  }

  const topConcepts = store.getSubjects(SKOS_TOP_CONCEPT_OF, namedNode(conceptSchemeIri), null)

  for (const topConcept of topConcepts) {
    getChildren(topConcept.value, conceptSchemeNode)
  }

  if (conceptSchemeLabel !== null) {
    treeNodes.value.push(conceptSchemeNode)
  }
}
</script>

<template>
  <div v-if="treeNodes">
    <Toast />
    <Accordion class="mt-4" :activeIndex="0">
      <AccordionTab header="Vocabulary Hierarchy">
        <div class="grid grid-cols-2 gap-4">
          <Tree
            v-model:selectionKeys="selectedKey"
            :value="treeNodes"
            selectionMode="single"
            :metaKeySelection="false"
            @node-select="handleNodeSelect"
            @node-unselect="handleNodeUnselect"
          />
          <pre v-if="selectedNodeTurtleValue">{{ selectedNodeTurtleValue }}</pre>
          <ProgressSpinner v-if="isTurtleCodeLoading" />
        </div>
      </AccordionTab>
    </Accordion>
  </div>
</template>
