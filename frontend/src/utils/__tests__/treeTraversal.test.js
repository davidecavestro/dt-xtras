import { findReachableTags } from '../treeTraversal.js';

describe('findReachableTags', () => {
  describe('Basic functionality', () => {
    test('should return empty set for null startNodeId', () => {
      const treeData = [
        { id: 'brand:acme', name: 'acme', children: [] }
      ];
      const result = findReachableTags(null, treeData);
      expect(result.size).toBe(0);
    });

    test('should return empty set for empty treeData', () => {
      const result = findReachableTags('brand:acme', []);
      expect(result.size).toBe(0);
    });

    test('should return empty set for null treeData', () => {
      const result = findReachableTags('brand:acme', null);
      expect(result.size).toBe(0);
    });
  });

  describe('Single node tree', () => {
    test('should return the node itself when no children', () => {
      const treeData = [
        { id: 'brand:acme', name: 'acme', children: [] }
      ];
      const result = findReachableTags('brand:acme', treeData);
      expect(result.size).toBe(1);
      expect(result.has('brand:acme')).toBe(true);
    });
  });

  describe('Two-level hierarchy', () => {
    test('should return parent and child nodes', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: [
            { id: 'region:us', name: 'us', children: [] }
          ]
        }
      ];
      const result = findReachableTags('brand:acme', treeData);
      expect(result.size).toBe(2);
      expect(result.has('brand:acme')).toBe(true);
      expect(result.has('region:us')).toBe(true);
    });

    test('should return only child when starting from child', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: [
            { id: 'region:us', name: 'us', children: [] }
          ]
        }
      ];
      const result = findReachableTags('region:us', treeData);
      expect(result.size).toBe(1);
      expect(result.has('region:us')).toBe(true);
      expect(result.has('brand:acme')).toBe(false);
    });
  });

  describe('Multi-level hierarchy', () => {
    test('should traverse all descendants', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: [
            {
              id: 'region:us',
              name: 'us',
              children: [
                { id: 'site:us-east', name: 'us-east', children: [] },
                { id: 'site:us-west', name: 'us-west', children: [] }
              ]
            }
          ]
        }
      ];
      const result = findReachableTags('brand:acme', treeData);
      expect(result.size).toBe(4);
      expect(result.has('brand:acme')).toBe(true);
      expect(result.has('region:us')).toBe(true);
      expect(result.has('site:us-east')).toBe(true);
      expect(result.has('site:us-west')).toBe(true);
    });

    test('should not traverse upward to parent', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: [
            {
              id: 'region:us',
              name: 'us',
              children: [
                { id: 'site:us-east', name: 'us-east', children: [] }
              ]
            }
          ]
        }
      ];
      const result = findReachableTags('region:us', treeData);
      expect(result.size).toBe(2);
      expect(result.has('region:us')).toBe(true);
      expect(result.has('site:us-east')).toBe(true);
      expect(result.has('brand:acme')).toBe(false);
    });
  });

  describe('Multiple root nodes', () => {
    test('should find correct subtree in multi-root tree', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: [
            { id: 'region:us', name: 'us', children: [] }
          ]
        },
        {
          id: 'brand:foo',
          name: 'foo',
          children: [
            { id: 'region:eu', name: 'eu', children: [] }
          ]
        }
      ];
      const result = findReachableTags('brand:acme', treeData);
      expect(result.size).toBe(2);
      expect(result.has('brand:acme')).toBe(true);
      expect(result.has('region:us')).toBe(true);
      expect(result.has('brand:foo')).toBe(false);
      expect(result.has('region:eu')).toBe(false);
    });
  });

  describe('Complete tag values vs labels', () => {
    test('should return complete tag IDs, not display names', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: [
            { id: 'region:us', name: 'us', children: [] }
          ]
        }
      ];
      const result = findReachableTags('brand:acme', treeData);
      expect(result.has('brand:acme')).toBe(true);
      expect(result.has('acme')).toBe(false);
      expect(result.has('region:us')).toBe(true);
      expect(result.has('us')).toBe(false);
    });
  });

  describe('Complex real-world scenario', () => {
    test('should handle hierarchical taxonomy structure', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: [
            {
              id: 'region:us',
              name: 'us',
              children: [
                {
                  id: 'site:acme:us:bundle:1.0.0',
                  name: '1.0.0',
                  children: []
                }
              ]
            },
            {
              id: 'region:eu',
              name: 'eu',
              children: [
                {
                  id: 'site:acme:eu:bundle:1.0.0',
                  name: '1.0.0',
                  children: []
                }
              ]
            }
          ]
        }
      ];
      const result = findReachableTags('brand:acme', treeData);
      expect(result.size).toBe(5);
      expect(result.has('brand:acme')).toBe(true);
      expect(result.has('region:us')).toBe(true);
      expect(result.has('region:eu')).toBe(true);
      expect(result.has('site:acme:us:bundle:1.0.0')).toBe(true);
      expect(result.has('site:acme:eu:bundle:1.0.0')).toBe(true);
    });
  });
});
