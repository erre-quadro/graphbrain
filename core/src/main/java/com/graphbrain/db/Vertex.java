package com.graphbrain.db;

import java.util.HashMap;
import java.util.Map;

public abstract class Vertex {

    protected String id;

    protected int degree;

    protected long ts;

    public abstract VertexType type();

    public Vertex(String id, int degree, long ts) {
        this.id = id;
        this.degree = degree;
        this.ts = ts;
    }

    public Vertex(String id) {
        this(id, 0, -1);
    }

    public Vertex(String id, Map<String, String> map) {
        this(id,
                Integer.parseInt(map.get("degree")),
                Long.parseLong(map.get("ts")));
    }

    public abstract Vertex copy();

    protected void fillMap(Map<String, String> map) {}

    public Map<String, String> toMap() {
        HashMap<String, String> map = new HashMap<String, String>();
        map.put("degree", "" + degree);
        map.put("ts", "" + ts);

        fillMap(map);

        return map;
    }

    public Vertex toGlobal() {
        Vertex r = copy();
        r.id = ID.userToGlobal(id);
        return r;
    }

    public Vertex toUser(String userId) {
        Vertex r = copy();
        r.id = ID.globalToUser(id, userId);
        return r;
    }

    @Override
    public String toString() {
        return id;
    }

    public String raw() {
        return "";
    }

    public Vertex updateFromEdges() {
        return this;
    }

    public static String cleanId(String id) {
        return id.toLowerCase();
    }

    public static Vertex fromId(String id) {
        switch(VertexType.getType(id)) {
            case Entity: return new EntityNode(id);
            case Edge: return Edge.fromId(id);
            case EdgeType: return new EdgeType(id);
            case URL: return new URLNode(id);
            case Prog: return new ProgNode(id, "");
            case User: return null; // this shouldn't happen
        }

        // shouldn't happen
        return null;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj instanceof Vertex) {
            Vertex that = (Vertex)obj;
            return that.id.equals(id);
        }

        return false;
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }

    public long getTs() {
        return ts;
    }

    public Vertex setTs(long ts) {
        this.ts = ts;
        return this;
    }

    public int getDegree() {
        return degree;
    }

    public Vertex setDegree(int degree) {
        this.degree = degree;
        return this;
    }
}