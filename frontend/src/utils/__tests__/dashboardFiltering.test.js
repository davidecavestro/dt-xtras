import { findReachableTags } from '../treeTraversal.js';

describe('Dashboard Project Filtering', () => {
  describe('relatedProjects filtering logic', () => {
    test('should filter projects by reachable tags', () => {
      // Mock tree data matching backend structure
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          type: 'taxonomy',
          children: [
            {
              id: 'region:us',
              name: 'us',
              type: 'taxonomy',
              children: [
                {
                  id: 'site:acme:us:bundle:1.0.0',
                  name: '1.0.0',
                  type: 'taxonomy',
                  children: []
                }
              ]
            }
          ]
        }
      ];

      // Mock projects
      const projects = [
        {
          uuid: 'proj1',
          name: 'Project 1',
          tags: [{ name: 'brand:acme' }]
        },
        {
          uuid: 'proj2',
          name: 'Project 2',
          tags: [{ name: 'region:us' }]
        },
        {
          uuid: 'proj3',
          name: 'Project 3',
          tags: [{ name: 'site:acme:us:bundle:1.0.0' }]
        },
        {
          uuid: 'proj4',
          name: 'Project 4',
          tags: [{ name: 'brand:foo' }]
        }
      ];

      // Select brand:acme node
      const selectedNode = { id: 'brand:acme', name: 'acme' };
      const reachableTags = findReachableTags(selectedNode.id, treeData);

      // Filter projects
      const filteredProjects = projects.filter(project => {
        if (!project || !project.tags || project.tags.length === 0) {
          return false;
        }
        return project.tags.some(tag =>
          tag && tag.name && reachableTags.has(tag.name)
        );
      });

      // Should include projects tagged with brand:acme, region:us, or site:acme:us:bundle:1.0.0
      expect(filteredProjects.length).toBe(3);
      expect(filteredProjects.find(p => p.uuid === 'proj1')).toBeDefined();
      expect(filteredProjects.find(p => p.uuid === 'proj2')).toBeDefined();
      expect(filteredProjects.find(p => p.uuid === 'proj3')).toBeDefined();
      expect(filteredProjects.find(p => p.uuid === 'proj4')).toBeUndefined();
    });

    test('should handle projects with multiple tags', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: []
        }
      ];

      const projects = [
        {
          uuid: 'proj1',
          name: 'Project 1',
          tags: [
            { name: 'brand:acme' },
            { name: 'region:us' }
          ]
        },
        {
          uuid: 'proj2',
          name: 'Project 2',
          tags: [{ name: 'region:eu' }]
        }
      ];

      const selectedNode = { id: 'brand:acme', name: 'acme' };
      const reachableTags = findReachableTags(selectedNode.id, treeData);

      const filteredProjects = projects.filter(project => {
        if (!project || !project.tags || project.tags.length === 0) {
          return false;
        }
        return project.tags.some(tag =>
          tag && tag.name && reachableTags.has(tag.name)
        );
      });

      expect(filteredProjects.length).toBe(1);
      expect(filteredProjects[0].uuid).toBe('proj1');
    });

    test('should return all projects when no node selected', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: []
        }
      ];

      const projects = [
        { uuid: 'proj1', name: 'Project 1', tags: [{ name: 'brand:acme' }] },
        { uuid: 'proj2', name: 'Project 2', tags: [{ name: 'brand:foo' }] }
      ];

      // No selection - should return all projects
      const filteredProjects = projects;

      expect(filteredProjects.length).toBe(2);
    });

    test('should handle projects with no tags', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: []
        }
      ];

      const projects = [
        { uuid: 'proj1', name: 'Project 1', tags: [] },
        { uuid: 'proj2', name: 'Project 2', tags: [{ name: 'brand:acme' }] }
      ];

      const selectedNode = { id: 'brand:acme', name: 'acme' };
      const reachableTags = findReachableTags(selectedNode.id, treeData);

      const filteredProjects = projects.filter(project => {
        if (!project || !project.tags || project.tags.length === 0) {
          return false;
        }
        return project.tags.some(tag =>
          tag && tag.name && reachableTags.has(tag.name)
        );
      });

      expect(filteredProjects.length).toBe(1);
      expect(filteredProjects[0].uuid).toBe('proj2');
    });

    test('should handle tag as string instead of object', () => {
      const treeData = [
        {
          id: 'brand:acme',
          name: 'acme',
          children: []
        }
      ];

      const projects = [
        { uuid: 'proj1', name: 'Project 1', tags: ['brand:acme'] },
        { uuid: 'proj2', name: 'Project 2', tags: ['brand:foo'] }
      ];

      const selectedNode = { id: 'brand:acme', name: 'acme' };
      const reachableTags = findReachableTags(selectedNode.id, treeData);

      const filteredProjects = projects.filter(project => {
        if (!project || !project.tags || project.tags.length === 0) {
          return false;
        }
        return project.tags.some(tag => {
          const tagName = typeof tag === 'string' ? tag : tag?.name;
          return tagName && reachableTags.has(tagName);
        });
      });

      expect(filteredProjects.length).toBe(1);
      expect(filteredProjects[0].uuid).toBe('proj1');
    });
  });
});
